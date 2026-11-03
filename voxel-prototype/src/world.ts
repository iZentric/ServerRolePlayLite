export const CHUNK_SIZE = 16;
export const WORLD_HEIGHT = 256;
const VOXELS_PER_CHUNK = CHUNK_SIZE * CHUNK_SIZE * WORLD_HEIGHT;

type Chunk = { x: number; z: number; blocks: Uint16Array };

export class World {
  private readonly chunks = new Map<string, Chunk>();

  get chunkCount(): number { return this.chunks.size; }

  getBlock(x: number, y: number, z: number): number {
    if (!Number.isInteger(x) || !Number.isInteger(y) || !Number.isInteger(z))
      throw new RangeError('voxel coordinates must be integers');
    if (y < 0 || y >= WORLD_HEIGHT) return 0;
    const cx = Math.floor(x / CHUNK_SIZE), cz = Math.floor(z / CHUNK_SIZE);
    const chunk = this.chunks.get(`${cx},${cz}`);
    return chunk?.blocks[(y * CHUNK_SIZE + z - cz * CHUNK_SIZE) * CHUNK_SIZE + x - cx * CHUNK_SIZE] ?? 0;
  }

  setBlock(x: number, y: number, z: number, id: number): void {
    if (![x, y, z, id].every(Number.isInteger) || y < 0 || y >= WORLD_HEIGHT || id < 0 || id > 65535)
      throw new RangeError('invalid voxel coordinates or block id');
    const cx = Math.floor(x / CHUNK_SIZE), cz = Math.floor(z / CHUNK_SIZE);
    const key = `${cx},${cz}`;
    let chunk = this.chunks.get(key);
    if (!chunk) {
      if (id === 0) return;
      chunk = { x: cx, z: cz, blocks: new Uint16Array(VOXELS_PER_CHUNK) };
      this.chunks.set(key, chunk);
    }
    chunk.blocks[(y * CHUNK_SIZE + z - cz * CHUNK_SIZE) * CHUNK_SIZE + x - cx * CHUNK_SIZE] = id;
  }

  forEachBlock(visit: (x: number, y: number, z: number, id: number) => void): void {
    for (const chunk of this.chunks.values()) {
      for (let y = 0; y < WORLD_HEIGHT; y++) for (let z = 0; z < CHUNK_SIZE; z++) {
        const row = (y * CHUNK_SIZE + z) * CHUNK_SIZE;
        for (let x = 0; x < CHUNK_SIZE; x++) {
          const id = chunk.blocks[row + x];
          if (id) visit(chunk.x * CHUNK_SIZE + x, y, chunk.z * CHUNK_SIZE + z, id);
        }
      }
    }
  }
}

export function createDemoWorld(): World {
  const world = new World();
  for (let x = -3; x <= 3; x++) for (let z = -18; z <= -12; z++)
    world.setBlock(x, 0, z, 1);
  for (let y = 1; y <= 5; y++) for (let x = -1; x <= 0; x++) for (let z = -16; z <= -15; z++)
    world.setBlock(x, y, z, 3);
  for (let x = -2; x <= 1; x++) for (let z = -17; z <= -14; z++)
    world.setBlock(x, 6, z, 4);
  for (const side of [-1, 1]) for (let row = 0; row < 5; row++) {
    const originX = side < 0 ? -10 : 7;
    const originZ = 1 - row * 7;
    const height = 2 + (row * 3 + (side + 1)) % 4;
    for (let y = 0; y <= height; y++) for (let x = originX; x < originX + 3; x++)
      for (let z = originZ; z < originZ + 3; z++)
        world.setBlock(x, y, z, y === height ? 4 : row % 2 ? 5 : 2);
  }
  return world;
}
