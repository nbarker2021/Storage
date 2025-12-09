
# GeoTokenizer Tie-In v1

A geometry-first token codec + memory manager for the Geometry-Only Transformer v2.

## Capabilities
- Encode/decode lists of points into compact bytes (quantized + varints + zlib).
- Break/extend/combine/refine token sequences.
- Learn "equivalence tokens" from past data and convert new inputs to canonical tokens.
- Merkle-chained ledger of operations (`.geo_tokenizer/ledger.jsonl`).

## CLI
```bash
# encode/decode
python geo_tokenizer_tiein_v1.py encode --in-json pts.json --out shape.geo
python geo_tokenizer_tiein_v1.py decode --in shape.geo --out-json pts_out.json

# learn a prototype and convert later inputs
python geo_tokenizer_tiein_v1.py learn --name HEX --from-json hex6.json
python geo_tokenizer_tiein_v1.py convert --from-json mystery.json

# synthesize/extend/refine/break
python geo_tokenizer_tiein_v1.py synthesize --n 8 --k 3
python geo_tokenizer_tiein_v1.py extend --from-json partial.json --target-n 12
python geo_tokenizer_tiein_v1.py refine --from-json trace.json --iters 3
python geo_tokenizer_tiein_v1.py break --from-json trace.json --idx 10
```
