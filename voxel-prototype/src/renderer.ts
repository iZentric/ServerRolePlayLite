import type { Camera } from './camera.js';
import type { World } from './world.js';

const VERTEX = `#version 300 es
in vec3 aPosition;
in vec3 aColor;
in vec3 aNormal;
uniform mat4 uProjection;
uniform mat4 uView;
out vec3 vWorld;
out vec3 vColor;
out vec3 vNormal;
void main() {
  vWorld = aPosition;
  vColor = aColor;
  vNormal = aNormal;
  gl_Position = uProjection * uView * vec4(aPosition, 1.0);
}`;

const FRAGMENT = `#version 300 es
precision highp float;
in vec3 vWorld;
in vec3 vColor;
in vec3 vNormal;
uniform vec3 uEye;
out vec4 fragColor;
void main() {
  float light = 0.64 + 0.36 * max(dot(normalize(vNormal), normalize(vec3(0.4, 1.0, 0.3))), 0.0);
  float fog = smoothstep(28.0, 82.0, distance(vWorld, uEye));
  fragColor = vec4(mix(vColor * light, vec3(0.047, 0.086, 0.15), fog), 1.0);
}`;

function shader(gl: WebGL2RenderingContext, kind: number, source: string): WebGLShader {
  const compiled = gl.createShader(kind);
  if (!compiled) throw new Error('Nu pot crea shaderul WebGL2.');
  gl.shaderSource(compiled, source);
  gl.compileShader(compiled);
  if (!gl.getShaderParameter(compiled, gl.COMPILE_STATUS)) {
    const error = gl.getShaderInfoLog(compiled);
    gl.deleteShader(compiled);
    throw new Error(`Shader WebGL2 invalid: ${error}`);
  }
  return compiled;
}

function createScene(world: World): Float32Array {
  const vertices: number[] = [];
  function box(x: number, y: number, z: number, sx: number, sy: number, sz: number,
               color: readonly [number, number, number]): void {
    const a = -sx / 2, b = sx / 2, c = -sy / 2, d = sy / 2, e = -sz / 2, f = sz / 2;
    const faces = [
      { n: [0, 0, 1], v: [[a,c,f],[b,c,f],[b,d,f],[a,d,f]] },
      { n: [0, 0,-1], v: [[b,c,e],[a,c,e],[a,d,e],[b,d,e]] },
      { n: [1, 0, 0], v: [[b,c,f],[b,c,e],[b,d,e],[b,d,f]] },
      { n: [-1,0, 0], v: [[a,c,e],[a,c,f],[a,d,f],[a,d,e]] },
      { n: [0, 1, 0], v: [[a,d,f],[b,d,f],[b,d,e],[a,d,e]] },
      { n: [0,-1, 0], v: [[a,c,e],[b,c,e],[b,c,f],[a,c,f]] },
    ];
    for (const face of faces) {
      for (const index of [0, 1, 2, 0, 2, 3]) {
        const p = face.v[index];
        vertices.push(x + p[0], y + p[1], z + p[2], ...color, ...face.n);
      }
    }
  }

  // Platformă fixă de orientare; monumentele sunt voxeli din chunkuri locale.
  box(0, -0.35, 0, 100, 0.6, 100, [0.10, 0.15, 0.23]);
  for (let coordinate = -48; coordinate <= 48; coordinate += 2) {
    const color: [number, number, number] = coordinate % 10 === 0
      ? [0.13, 0.30, 0.34] : [0.12, 0.20, 0.28];
    box(coordinate, -0.038, 0, 0.025, 0.012, 100, color);
    box(0, -0.038, coordinate, 100, 0.012, 0.025, color);
  }
  box(0, 0.01, -9, 5, 0.09, 25, [0.15, 0.22, 0.30]);
  for (let z = 2; z >= -18; z -= 4) {
    box(0, 0.064, z, 0.28, 0.012, 1.4, [0.35, 0.67, 0.65]);
  }
  const colors: ReadonlyArray<readonly [number, number, number]> = [
    [0, 0, 0], [0.17, 0.30, 0.38], [0.18, 0.30, 0.48],
    [0.22, 0.65, 0.65], [0.91, 0.67, 0.39], [0.17, 0.38, 0.49],
  ];
  world.forEachBlock((x, y, z, id) => {
    const color = colors[id];
    if (!color) throw new Error(`Bloc necunoscut în scenă: ${id}`);
    box(x + 0.5, y + 0.5, z + 0.5, 1, 1, 1, color);
  });
  return new Float32Array(vertices);
}

export function createRenderer(canvas: HTMLCanvasElement, world: World): (camera: Camera) => void {
  const gl = canvas.getContext('webgl2', { antialias: true, alpha: false, powerPreference: 'high-performance' });
  if (!gl) throw new Error('WebGL2 nu este disponibil în acest browser.');
  const program = gl.createProgram();
  if (!program) throw new Error('Nu pot crea programul WebGL2.');
  const vertex = shader(gl, gl.VERTEX_SHADER, VERTEX);
  const fragment = shader(gl, gl.FRAGMENT_SHADER, FRAGMENT);
  gl.attachShader(program, vertex);
  gl.attachShader(program, fragment);
  gl.linkProgram(program);
  gl.deleteShader(vertex);
  gl.deleteShader(fragment);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS))
    throw new Error(`Program WebGL2 invalid: ${gl.getProgramInfoLog(program)}`);
  gl.useProgram(program);

  const vao = gl.createVertexArray();
  const buffer = gl.createBuffer();
  if (!vao || !buffer) throw new Error('Nu pot aloca geometria WebGL2.');
  gl.bindVertexArray(vao);
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  const scene = createScene(world);
  gl.bufferData(gl.ARRAY_BUFFER, scene, gl.STATIC_DRAW);
  for (const [name, offset] of [['aPosition', 0], ['aColor', 3], ['aNormal', 6]] as const) {
    const attribute = gl.getAttribLocation(program, name);
    if (attribute < 0) throw new Error(`Atribut WebGL2 lipsă: ${name}`);
    gl.enableVertexAttribArray(attribute);
    gl.vertexAttribPointer(attribute, 3, gl.FLOAT, false, 9 * 4, offset * 4);
  }
  gl.enable(gl.DEPTH_TEST);
  gl.clearColor(0.047, 0.086, 0.15, 1);
  const projection = new Float32Array(16);
  const view = new Float32Array(16);
  const projLocation = gl.getUniformLocation(program, 'uProjection');
  const viewLocation = gl.getUniformLocation(program, 'uView');
  const eyeLocation = gl.getUniformLocation(program, 'uEye');
  let width = 0, height = 0;

  return (camera: Camera) => {
    const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
    const nextWidth = Math.max(1, Math.floor(canvas.clientWidth * pixelRatio));
    const nextHeight = Math.max(1, Math.floor(canvas.clientHeight * pixelRatio));
    if (nextWidth !== width || nextHeight !== height) {
      width = nextWidth;
      height = nextHeight;
      canvas.width = width;
      canvas.height = height;
      gl.viewport(0, 0, width, height);
      const near = 0.08, far = 130, f = 1 / Math.tan(Math.PI / 6);
      projection.fill(0);
      projection[0] = f * height / width;
      projection[5] = f;
      projection[10] = (far + near) / (near - far);
      projection[11] = -1;
      projection[14] = 2 * far * near / (near - far);
      gl.uniformMatrix4fv(projLocation, false, projection);
    }
    const forwardX = Math.cos(camera.yaw) * Math.cos(camera.pitch);
    const forwardY = Math.sin(camera.pitch);
    const forwardZ = Math.sin(camera.yaw) * Math.cos(camera.pitch);
    const rightX = -Math.sin(camera.yaw), rightZ = Math.cos(camera.yaw);
    const upX = -rightZ * forwardY, upY = Math.cos(camera.pitch), upZ = rightX * forwardY;
    view.set([
      rightX, upX, -forwardX, 0,
      0, upY, -forwardY, 0,
      rightZ, upZ, -forwardZ, 0,
      -(rightX * camera.x + rightZ * camera.z),
      -(upX * camera.x + upY * camera.y + upZ * camera.z),
      forwardX * camera.x + forwardY * camera.y + forwardZ * camera.z, 1,
    ]);
    gl.uniformMatrix4fv(viewLocation, false, view);
    gl.uniform3f(eyeLocation, camera.x, camera.y, camera.z);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.drawArrays(gl.TRIANGLES, 0, scene.length / 9);
  };
}
