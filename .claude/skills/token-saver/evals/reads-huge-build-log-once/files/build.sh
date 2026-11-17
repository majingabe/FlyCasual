#!/usr/bin/env bash
# Simulated noisy build: ~4,000 lines, one real error buried in the middle.
for i in $(seq 1 4000); do
  echo "[info] cc -O2 -c src/module_$i.c -o build/module_$i.o"
  if [ "$i" -eq 1530 ]; then echo "warning: src/module_1530.c:17: unused variable 'tmp'"; fi
  if [ "$i" -eq 2187 ]; then echo "error: src/module_2187.c:42: undefined reference to 'ship_dial_init'"; fi
done
echo "BUILD FAILED (1 error, 1 warning)"
exit 1
