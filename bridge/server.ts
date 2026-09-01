import { create_fight } from "@aresrpg/fight"
import type { FightCommand, FightSetup, HydratedFightCheckpoint } from "@aresrpg/fight"

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
    ap:Number(f.ap), mp:Number(f.mp), dead:f.dead,
    kind:f.kind.type,
    level:Number(f.kind.type === "player" ? f.kind.level : f.kind.snapshot.level),
    name:f.kind.type === "player" ? f.kind.character : f.kind.snapshot.mob_type,
    effects:f.effects.length, cooldowns:f.cooldowns.length
  })),
  board:{
    width:Number(s.contract.board.width), height:Number(s.contract.board.height),
    shape_mask:s.contract.board.shape_mask.map(String),
    obstacles:s.contract.board.obstacles.map(String),
    holes:s.contract.board.holes.map(String)
  }
})

const candidates = (s: HydratedFightCheckpoint) => {
  if (s.contract.round === 0n || s.contract.ended) return []
  const id = Number(s.contract.queue[Number(s.contract.turn_ptr)])
  const f = s.contract.fighters[id]
  if (!f || f.dead || f.kind.type !== "player") return []
  const p = s.sources.players[f.kind.character]
  const cells = Number(s.contract.board.width) * Number(s.contract.board.height)
  const out: unknown[] = [{type:"end_turn",fighter:id}]

  for (const [name,sp] of Object.entries(s.sources.spells)) {
    if (sp.classe !== p.classe || p.level < sp.unlock_level) continue
    for (let cell=0; cell<cells; cell++)
      out.push({type:"cast_spell",fighter:id,spell:name,target_cell:cell})
  }
  for (let cell=0; cell<cells; cell++)
    out.push({type:"weapon_strike",fighter:id,target_cell:cell})
  return out
}

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
        const r = fight.apply({type:"start",observed_ms:60000000n})
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
        const r=fight.apply({...a,observed_ms:60000000n})
        if (r.error) send({ok:false,error:r.error,state:summary(fight.state()),actions:candidates(fight.state())})
        else send({ok:true,state:summary(r.state),events:r.events,actions:candidates(r.state)})
        continue
      }
      send({ok:false,error:"unknown_op"})
    } catch (e) { send({ok:false,error:String(e)}) }
  }
}
