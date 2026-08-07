import { describe, it, expect, vi, beforeEach } from "vitest";
import { EventEmitter } from "events";

vi.mock("child_process", () => ({
  spawn: vi.fn(),
}));

import { spawn } from "child_process";
import { spawnPython } from "../src/utils/subprocess.js";

function makeFakeProc() {
  const proc = new EventEmitter() as EventEmitter & {
    stdout: EventEmitter;
    stderr: EventEmitter;
    stdin: { write: (s: string) => void; end: () => void };
  };
  proc.stdout = new EventEmitter();
  proc.stderr = new EventEmitter();
  proc.stdin = { write: vi.fn(), end: vi.fn() };
  return proc;
}

describe("spawnPython", () => {
  beforeEach(() => {
    vi.mocked(spawn).mockReset();
  });

  it("rejects the promise instead of throwing when the subprocess fails to spawn", async () => {
    const fakeProc = makeFakeProc();
    vi.mocked(spawn).mockReturnValue(fakeProc as never);

    const promise = spawnPython("does_not_matter.py", {});

    expect(() => fakeProc.emit("error", new Error("spawn python ENOENT"))).not.toThrow();
    await expect(promise).rejects.toThrow(/ENOENT/);
  });

  it("still resolves normally on a successful run", async () => {
    const fakeProc = makeFakeProc();
    vi.mocked(spawn).mockReturnValue(fakeProc as never);

    const promise = spawnPython("does_not_matter.py", {});
    fakeProc.stdout.emit("data", Buffer.from('{"ok":true}'));
    fakeProc.emit("close", 0);

    await expect(promise).resolves.toEqual({ ok: true });
  });
});
