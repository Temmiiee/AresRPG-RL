import type { FightCommand, FightSetup, HydratedFightCheckpoint } from "@aresrpg/fight"

// @aresrpg/fight is a private, unpublished workspace package (not on npm), so it can't
// be resolved through node_modules from here. It also has zero runtime dependencies of
// its own, so importing its source directly from the AresRPG checkout — no `bun install`
// of the whole monorepo required — is both correct and the lighter-weight option.
// `@aresrpg/fight` above is a type-only import: it resolves for editors/tsc only if
// the AresRPG repo happens to be linked locally, and is fully elided at runtime.
const ARES_RPG_ROOT = process.env.ARES_RPG_ROOT
if (!ARES_RPG_ROOT) throw new Error("Set ARES_RPG_ROOT first.")
const {
  create_fight, reachable_fight_cells, fight_path_to, spell_target_cells, weapon_target_cells, player_max_hp,
  CONTRACT_CONSTANTS,
} = (await import(`${ARES_RPG_ROOT}/packages/fight/src/index.ts`)) as typeof import("@aresrpg/fight")

const bigintify = (v: unknown): unknown => {
  if (Array.isArray(v)) return v.map(bigintify)
  if (v && typeof v === "object")
    return Object.fromEntries(Object.entries(v).map(([k,x]) => [k,bigintify(x)]))
  if (typeof v === "string" && /^-?\d+n$/.test(v)) return BigInt(v.slice(0,-1))
  return v
}
const stringify = (v: unknown) =>
  JSON.stringify(v, (_, x) => typeof x === "bigint" ? `${x}n` : x)

const send = (v: unknown) => process.stdout.write(stringify(v) + "\n")

const summary = (s: HydratedFightCheckpoint) => ({
  ended: s.contract.ended,
  winner: s.contract.winner === null ? null : Number(s.contract.winner),
  round: Number(s.contract.round),
  turn: s.contract.round === 0n ? null :
    Number(s.contract.queue[Number(s.contract.turn_ptr)]),
  fighters: s.contract.fighters.map((f,i) => ({
    id:i, team:Number(f.team), cell:Number(f.cell), hp:Number(f.hp),
    // max_hp: fighters only ever store current hp; a player's cap is a property of their
    // source+level (player_max_hp), a mob's is already on its snapshot.
    max_hp:Number(f.kind.type === "player" ? player_max_hp(s.sources.players[f.kind.character]) : f.kind.snapshot.max_hp),
    ap:Number(f.ap), mp:Number(f.mp), dead:f.dead,
    kind:f.kind.type,
    level:Number(f.kind.type === "player" ? f.kind.level : f.kind.snapshot.level),
    name:f.kind.type === "player" ? f.kind.character : f.kind.snapshot.mob_type,
    classe:f.kind.type === "player" ? s.sources.players[f.kind.character].classe : null,
    effects:f.effects.length, cooldowns:f.cooldowns.length
  })),
  board:{
    width:Number(s.contract.board.width), height:Number(s.contract.board.height),
    shape_mask:s.contract.board.shape_mask.map(String),
    obstacles:s.contract.board.obstacles.map(String),
    holes:s.contract.board.holes.map(String),
    // The fixed combat-grid dimensions a `cell` index decodes against (x = cell % grid_w,
    // y = cell / grid_w) — NOT the same as width/height above, which describe this fight's
    // playable shape's bounding box within that fixed grid.
    grid_w:Number(CONTRACT_CONSTANTS.grid_w), grid_h:Number(CONTRACT_CONSTANTS.grid_h)
  }
})

const candidates = (s: HydratedFightCheckpoint) => {
  if (s.contract.round === 0n || s.contract.ended) return []
  const id = Number(s.contract.queue[Number(s.contract.turn_ptr)])
  // `fighter`/`target_cell` must be real BigInt here, not plain numbers: the engine
  // compares them against bigint queue/cell values with strict `===`, which is always
  // false across types (1n === 1 is false in JS) — a plain number silently loses every
  // action to a "not_your_fighter"/mismatch rejection instead of an obvious crash.
  const seat = BigInt(id)
  const f = s.contract.fighters[id]
  if (!f || f.dead || f.kind.type !== "player") return []
  const p = s.sources.players[f.kind.character]
  const out: unknown[] = [{type:"end_turn",fighter:seat}]

  for (const target of reachable_fight_cells(s, seat)) {
    const path = fight_path_to(s, seat, target)
    if (path) out.push({type:"move_to",fighter:seat,path})
  }

  // spell_target_cells/weapon_target_cells run the engine's real cast_legality check
  // (AP, range, line of sight/launch, cooldowns, cast caps) per cell, so this enumerates
  // the actual legal targets instead of every board cell and hoping the engine rejects
  // the illegal ones later.
  for (const [name,sp] of Object.entries(s.sources.spells)) {
    if (sp.classe !== p.classe || p.level < sp.unlock_level) continue
    for (const cell of spell_target_cells(s, seat, name).targetable)
      out.push({type:"cast_spell",fighter:seat,spell:name,target_cell:cell})
  }
  for (const cell of weapon_target_cells(s, seat).targetable)
    out.push({type:"weapon_strike",fighter:seat,target_cell:cell})
  return out
}

// A monotonic virtual clock, not wall-clock time: end_turn is gated by turn_min_ms
// (3s, an anti-spam rule for live play) measured as observed_ms since the turn
// started. Training wants to blow through turns as fast as possible, so each
// request bumps this clock well past that gate instead of using real time.
let clock = 0n
const next_ms = (): bigint => { clock += 10_000n; return clock }

let fight: ReturnType<typeof create_fight> | null = null
const reader = Bun.stdin.stream().getReader()
const decoder = new TextDecoder()
let buffer = ""

while (true) {
  const {value,done} = await reader.read()
  if (done) break
  buffer += decoder.decode(value)
  const lines = buffer.split("\n")
  buffer = lines.pop() ?? ""
  for (const line of lines) {
    if (!line.trim()) continue
    try {
      const m = JSON.parse(line)
      if (m.op === "ping") { send({ok:true}); continue }
      if (m.op === "reset") {
        const setup = bigintify(m.setup) as FightSetup
        fight = create_fight({setup,mode:"local",seed:BigInt(m.seed ?? 1)})
        const r = fight.apply({type:"start",observed_ms:next_ms()})
        if (r.error) send({ok:false,error:r.error,state:summary(fight.state())})
        else send({ok:true,state:summary(r.state),actions:candidates(r.state)})
        continue
      }
      if (!fight) { send({ok:false,error:"not_initialized"}); continue }
      if (m.op === "state") {
        const s=fight.state(); send({ok:true,state:summary(s),actions:candidates(s)}); continue
      }
      if (m.op === "step") {
        const a=bigintify(m.action) as FightCommand
        const r=fight.apply({...a,observed_ms:next_ms()})
        if (r.error) send({ok:false,error:r.error,state:summary(fight.state()),actions:candidates(fight.state())})
        else send({ok:true,state:summary(r.state),events:r.events,actions:candidates(r.state)})
        continue
      }
      send({ok:false,error:"unknown_op"})
    } catch (e) { send({ok:false,error:String(e)}) }
  }
}
