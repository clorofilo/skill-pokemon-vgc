import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CALC_TOOLS_DIR = path.resolve(__dirname, "../../../calc-tools");

const SPAWN_TIMEOUT_MS = 15_000;

export async function spawnPython(script: string, input: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(CALC_TOOLS_DIR, script);
    const proc = spawn("python", [scriptPath], {
      stdio: ["pipe", "pipe", "pipe"],
      cwd: CALC_TOOLS_DIR,
    });

    let stdout = "";
    let stderr = "";
    let settled = false;

    const timer = setTimeout(() => {
      if (settled) return;
      settled = true;
      proc.kill();
      reject(new Error(`Python script '${script}' timed out after ${SPAWN_TIMEOUT_MS}ms`));
    }, SPAWN_TIMEOUT_MS);

    proc.stdout.on("data", (chunk: Buffer) => (stdout += chunk.toString()));
    proc.stderr.on("data", (chunk: Buffer) => (stderr += chunk.toString()));

    proc.on("error", (err) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(new Error(`Failed to spawn python for '${script}': ${err.message}`));
    });

    proc.on("close", (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (code !== 0) {
        reject(new Error(`Python script '${script}' exited ${code}: ${stderr}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch {
        reject(new Error(`Invalid JSON from '${script}': ${stdout.slice(0, 200)}`));
      }
    });

    proc.stdin.write(JSON.stringify(input));
    proc.stdin.end();
  });
}
