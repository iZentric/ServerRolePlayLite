import { moveCamera, rotateCamera, type Camera } from './camera.js';
import { createRenderer } from './renderer.js';
import { createDemoWorld } from './world.js';
import './style.css';

const canvas = document.querySelector<HTMLCanvasElement>('#world')!;
const overlay = document.querySelector<HTMLElement>('#entry')!;
const startButton = document.querySelector<HTMLButtonElement>('#start')!;
const status = document.querySelector<HTMLElement>('#status')!;
const position = document.querySelector<HTMLElement>('#position')!;
const fps = document.querySelector<HTMLElement>('#fps')!;
const heading = document.querySelector<HTMLElement>('#heading')!;
const world = createDemoWorld();
document.querySelector<HTMLElement>('#chunks')!.textContent = String(world.chunkCount);
let render: ReturnType<typeof createRenderer>;
let camera: Camera = { x: 0, y: 2.1, z: 9, yaw: -Math.PI / 2, pitch: -0.08 };
const keys = new Set<string>();
let active = false;
let dragging = false;
let lastFrame = performance.now();
let frames = 0;
let fpsTime = lastFrame;
let hudTime = lastFrame;

function begin(): void {
  active = true;
  overlay.hidden = true;
  canvas.focus();
  status.textContent = 'EXPLORARE ACTIVĂ';
  // Pointer lock may be blocked by embedded previews; dragging and arrows still work.
  void canvas.requestPointerLock().catch(() => {
    status.textContent = 'EXPLORARE · PRIVIRE CU DRAG / SĂGEȚI';
  });
}

startButton.addEventListener('click', begin);
canvas.addEventListener('click', () => { if (!active) begin(); });
canvas.addEventListener('mousedown', () => { dragging = true; });
window.addEventListener('mouseup', () => { dragging = false; });
document.addEventListener('pointerlockchange', () => {
  if (document.pointerLockElement === canvas) {
    status.textContent = 'EXPLORARE ACTIVĂ';
  } else if (active && !dragging) {
    active = false;
    keys.clear();
    overlay.hidden = false;
    status.textContent = 'PAUZĂ · APASĂ PENTRU A REVENI';
  }
});
window.addEventListener('blur', () => { keys.clear(); dragging = false; });
window.addEventListener('keydown', (event) => {
  const key = event.key.toLowerCase();
  if (key === 'escape' && active && document.pointerLockElement !== canvas) {
    active = false;
    overlay.hidden = false;
    keys.clear();
  }
  if (active && ['w','a','s','d','q','e','arrowup','arrowdown','arrowleft','arrowright','shift',' '].includes(key))
    event.preventDefault();
  keys.add(key);
});
window.addEventListener('keyup', (event) => { keys.delete(event.key.toLowerCase()); });
window.addEventListener('mousemove', (event) => {
  if (active && (document.pointerLockElement === canvas || dragging))
    camera = rotateCamera(camera, event.movementX, event.movementY);
});

function frame(now: number): void {
  const dt = Math.min(Math.max((now - lastFrame) / 1000, 0), 0.05);
  lastFrame = now;
  if (active) {
    camera = moveCamera(camera, {
      forward: Number(keys.has('w')) - Number(keys.has('s')),
      strafe: Number(keys.has('d')) - Number(keys.has('a')),
      vertical: Number(keys.has(' ') || keys.has('e')) - Number(keys.has('q')),
      sprint: keys.has('shift'),
    }, dt);
    const lookSpeed = 850 * dt;
    camera = rotateCamera(camera,
      (Number(keys.has('arrowright')) - Number(keys.has('arrowleft'))) * lookSpeed,
      (Number(keys.has('arrowdown')) - Number(keys.has('arrowup'))) * lookSpeed);
  }
  render(camera);
  frames++;
  if (now - fpsTime >= 500) {
    fps.textContent = String(Math.round(frames * 1000 / (now - fpsTime)));
    frames = 0;
    fpsTime = now;
  }
  if (now - hudTime >= 100) {
    position.textContent = `${camera.x.toFixed(1)} / ${camera.y.toFixed(1)} / ${camera.z.toFixed(1)}`;
    heading.textContent = `${Math.round(((camera.yaw * 180 / Math.PI) % 360 + 360) % 360)}°`;
    hudTime = now;
  }
  requestAnimationFrame(frame);
}

try {
  render = createRenderer(canvas, world);
  requestAnimationFrame(frame);
} catch (error) {
  status.textContent = error instanceof Error ? error.message : 'Randarea nu a pornit.';
  startButton.disabled = true;
}
