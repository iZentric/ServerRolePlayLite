import test from 'node:test';
import assert from 'node:assert/strict';
import { moveCamera, rotateCamera, type Camera } from '../src/camera.js';

const starting: Camera = { x: 0, y: 2, z: 8, yaw: -Math.PI / 2, pitch: 0 };
const idle = { forward: 0, strafe: 0, vertical: 0, sprint: false };

test('forward faces negative Z; movement is frame-rate independent', () => {
  const once = moveCamera(starting, { ...idle, forward: 1 }, 1);
  const half = moveCamera(moveCamera(starting, { ...idle, forward: 1 }, .5),
    { ...idle, forward: 1 }, .5);
  assert.ok(Math.abs(once.z - 2.5) < 1e-9);
  assert.ok(Math.abs(once.x) < 1e-9);
  assert.ok(Math.abs(once.z - half.z) < 1e-9);
});

test('diagonal movement cannot exceed the base speed', () => {
  const moved = moveCamera(starting, { ...idle, forward: 1, strafe: 1 }, 1);
  assert.ok(Math.abs(Math.hypot(moved.x, moved.z - starting.z) - 5.5) < 1e-9);
});

test('sprint and vertical flight work without changing camera direction', () => {
  const moved = moveCamera(starting, { forward: 1, strafe: 0, vertical: 1, sprint: true }, 1);
  assert.equal(moved.y, 11);
  assert.ok(Math.abs(moved.z - (starting.z - 9)) < 1e-9);
  assert.equal(moved.yaw, starting.yaw);
});

test('look clamps pitch and does not mutate the previous camera', () => {
  const up = rotateCamera(starting, 50, -9999);
  assert.ok(up.pitch < Math.PI / 2 && up.pitch > 1.4);
  const down = rotateCamera(up, 0, 9999);
  assert.ok(down.pitch > -Math.PI / 2 && down.pitch < -1.4);
  assert.equal(starting.pitch, 0);
});
