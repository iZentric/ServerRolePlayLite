export type Camera = Readonly<{ x: number; y: number; z: number; yaw: number; pitch: number }>;
export type Movement = Readonly<{ forward: number; strafe: number; vertical: number; sprint: boolean }>;

const LOOK_SENSITIVITY = 0.0022;
const PITCH_LIMIT = 1.52;

export function rotateCamera(camera: Camera, mouseX: number, mouseY: number): Camera {
  return {
    ...camera,
    yaw: camera.yaw + mouseX * LOOK_SENSITIVITY,
    pitch: Math.max(-PITCH_LIMIT, Math.min(PITCH_LIMIT, camera.pitch - mouseY * LOOK_SENSITIVITY)),
  };
}

export function moveCamera(camera: Camera, input: Movement, seconds: number): Camera {
  if (!Number.isFinite(seconds) || seconds < 0) throw new RangeError('invalid frame time');
  const length = Math.max(1, Math.hypot(input.forward, input.strafe));
  const forward = input.forward / length;
  const strafe = input.strafe / length;
  const distance = (input.sprint ? 9 : 5.5) * seconds;
  return {
    ...camera,
    x: camera.x + (Math.cos(camera.yaw) * forward - Math.sin(camera.yaw) * strafe) * distance,
    y: camera.y + input.vertical * distance,
    z: camera.z + (Math.sin(camera.yaw) * forward + Math.cos(camera.yaw) * strafe) * distance,
  };
}
