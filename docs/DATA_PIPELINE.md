# Data pipeline

The fixture in `data/archetypes.json` is only a bootstrap.

The real pipeline should extract or define a versioned canonical dataset from AresRPG:

```text
AresRPG source/content
        |
        v
extractor
        |
        v
canonical JSON
        |
        +--> classes
        +--> spells
        +--> mobs
        +--> stats
        +--> weapons
        +--> maps/boards
        |
        v
scenario generator
```

Do not duplicate authoritative combat formulas in the dataset.

The dataset describes content. The fight engine decides combat behavior.

Every dataset snapshot should record:
- AresRPG commit;
- extraction date;
- schema version;
- source paths;
- transformation version.
