import test from 'node:test';
import assert from 'node:assert/strict';
import { World } from '../src/world.js';

test('empty reads do not allocate chunks and y stays in 0..255', () => {
  const world = new World();
  assert.equal(world.getBlock(0, 0, 0), 0);
  assert.equal(world.getBlock(0, -1, 0), 0);
  assert.equal(world.getBlock(0, 256, 0), 0);
  assert.equal(world.chunkCount, 0);
  assert.throws(() => world.setBlock(0, 256, 0, 1), RangeError);
  assert.equal(world.chunkCount, 0);
});

test('chunk boundaries including negative coordinates remain independent', () => {
  const world = new World();
  const positions = [[0, 0], [15, 15], [16, 0], [-1, -1], [-16, -16], [-17, -1]] as const;
  positions.forEach(([x, z], index) => world.setBlock(x, 255, z, index + 1));
  positions.forEach(([x, z], index) => assert.equal(world.getBlock(x, 255, z), index + 1));
  assert.equal(world.getBlock(1, 255, 1), 0);
  assert.equal(world.chunkCount, 4); // 0/15 and -1/-16 share their respective chunks.
});

test('overwrite and remove change only the selected voxel; iteration skips air', () => {
  const world = new World();
  world.setBlock(-1, 3, -1, 4);
  world.setBlock(-1, 3, -1, 6);
  world.setBlock(4, 0, 6, 2);
  const seen: Array<[number, number, number, number]> = [];
  world.forEachBlock((x, y, z, id) => seen.push([x, y, z, id]));
  assert.deepEqual(seen.sort(), [[-1, 3, -1, 6], [4, 0, 6, 2]].sort());
  world.setBlock(-1, 3, -1, 0);
  assert.equal(world.getBlock(-1, 3, -1), 0);
  assert.equal(world.chunkCount, 2);
  assert.throws(() => world.setBlock(0, 0, 0, 65536), RangeError);
});
