#!/usr/bin/env python3
"""Compile the *actual patched method* with Java 11, no Gradle/Minecraft jars.

Small type stubs only allow javac to run offline. The harness cannot prove
Forge/Bukkit/mod runtime compatibility. A deliberate source regression must
fail the same tests before the real method is accepted.
"""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HEADER = '''import java.util.ArrayList;
import java.util.List;

public class BridgeContract {
    static class World {}
    static class ServerWorld extends World {}
    static class Entity {}
    static class ServerPlayerEntity extends Entity {}
    static class Hand { static final Hand MAIN_HAND = new Hand(); }
    static class Direction { Direction getOpposite() { return this; } }
    static class BlockPos {
        BlockPos relative(Direction dir) { return this; }
        int getX() { return 0; }
        int getY() { return 0; }
        int getZ() { return 0; }
    }
    interface BlockState {}
    static class CraftBlockState implements BlockState {
        static CraftBlockState getBlockState(World world, BlockPos pos) { return new CraftBlockState(); }
    }
    static class BlockSnapshot { BlockPos getPos() { return new BlockPos(); } }
    static class BlockPlaceEvent {
        final boolean canceled, canBuild;
        BlockPlaceEvent(boolean canceled, boolean canBuild) {
            this.canceled = canceled; this.canBuild = canBuild;
        }
        boolean isCancelled() { return canceled; }
        boolean canBuild() { return canBuild; }
    }
    static class BlockEvent {
        static Hand hand;
        static Direction direction;
        static class EntityPlaceEvent {
            private boolean canceled;
            EntityPlaceEvent(boolean canceled) { this.canceled = canceled; }
            Object getEntity() { return new ServerPlayerEntity(); }
            BlockSnapshot getBlockSnapshot() { return new BlockSnapshot(); }
            BlockPos getPos() { return new BlockPos(); }
            World getWorld() { return new ServerWorld(); }
            boolean isCanceled() { return canceled; }
            void setCanceled(boolean value) { canceled = value; }
        }
        static class EntityMultiPlaceEvent extends EntityPlaceEvent {
            EntityMultiPlaceEvent(boolean canceled) { super(canceled); }
            List<BlockSnapshot> getReplacedBlockSnapshots() {
                List<BlockSnapshot> items = new ArrayList<>();
                items.add(new BlockSnapshot()); items.add(new BlockSnapshot());
                return items;
            }
        }
    }
    static class CraftEventFactory {
        static boolean cancel, build;
        static int singleCalls, multiCalls;
        static BlockPlaceEvent callBlockPlaceEvent(ServerWorld world, ServerPlayerEntity player,
                Hand hand, CraftBlockState state, int x, int y, int z) {
            singleCalls++;
            return new BlockPlaceEvent(cancel, build);
        }
        static BlockPlaceEvent callBlockMultiPlaceEvent(ServerWorld world, ServerPlayerEntity player,
                Hand hand, List<BlockState> states, int x, int y, int z) {
            if (states.size() != 2) throw new AssertionError("multi-place snapshots missing");
            multiCalls++;
            return new BlockPlaceEvent(cancel, build);
        }
    }
    static class UnderTest {
'''
FOOTER = '''    }
    public static void main(String[] args) {
        int cases = 0;
        for (boolean multi : new boolean[]{false, true}) {
            for (boolean forge : new boolean[]{false, true}) {
                for (boolean bukkit : new boolean[]{false, true}) {
                    for (boolean canBuild : new boolean[]{false, true}) {
                        CraftEventFactory.cancel = bukkit;
                        CraftEventFactory.build = canBuild;
                        CraftEventFactory.singleCalls = 0;
                        CraftEventFactory.multiCalls = 0;
                        BlockEvent.EntityPlaceEvent event = multi
                            ? new BlockEvent.EntityMultiPlaceEvent(forge)
                            : new BlockEvent.EntityPlaceEvent(forge);
                        new UnderTest().onBlockPlaceEvent(event);
                        boolean expected = forge || bukkit || !canBuild;
                        if (event.isCanceled() != expected ||
                                CraftEventFactory.singleCalls != (multi ? 0 : 1) ||
                                CraftEventFactory.multiCalls != (multi ? 1 : 0)) {
                            throw new AssertionError("Forge/Bukkit veto or callback regression");
                        }
                        cases++;
                    }
                }
            }
        }
        if (cases != 16) throw new AssertionError("missing case");
        System.out.println("JAVA11_BRIDGE_CONTRACT_PASS cases=" + cases);
    }
}
'''


def extract_method(text):
    start = text.index('public void onBlockPlaceEvent(BlockEvent.EntityPlaceEvent event) {')
    end = text.index('\n    @SubscribeEvent', start)
    method = text[start:end].strip()
    if (method.count('boolean forgeCanceled = event.isCanceled();') != 1 or
            method.count('event.setCanceled(forgeCanceled || bukkitEvent.isCancelled() || !bukkitEvent.canBuild());') != 1 or
            method.count('CraftEventFactory.callBlockPlaceEvent') != 1 or
            method.count('CraftEventFactory.callBlockMultiPlaceEvent') != 1):
        raise ValueError('not the pinned FunCity block-place method')
    return method


def run_contract(source, javac, java):
    method = extract_method(Path(source).read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='fc-bridge-contract-') as temp:
        root = Path(temp)
        java_file = root / 'BridgeContract.java'
        for mutant in (True, False):
            to_compile = method.replace('forgeCanceled || bukkitEvent.isCancelled()',
                                        'bukkitEvent.isCancelled()') if mutant else method
            java_file.write_text(HEADER + '        ' + to_compile + '\n' + FOOTER)
            compiler = subprocess.run([javac, '--release', '11', '-d', temp, str(java_file)],
                                      capture_output=True, timeout=60)
            if compiler.returncode:
                raise ValueError('Java11 compilation failed (no raw compiler log)')
            result = subprocess.run([java, '-cp', temp, 'BridgeContract'],
                                    capture_output=True, timeout=30)
            if mutant and result.returncode == 0:
                raise ValueError('deliberately broken Forge veto was not rejected')
            if not mutant and (result.returncode != 0 or
                               b'JAVA11_BRIDGE_CONTRACT_PASS cases=16' not in result.stdout):
                raise ValueError('real Forge/Bukkit veto failed Java11 contract')
    return True


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(2)
    try:
        run_contract(sys.argv[1], sys.argv[2], sys.argv[3])
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print('BRIDGE_JAVA11_CONTRACT_REJECTED: ' + str(exc), file=sys.stderr)
        sys.exit(2)
    print('BRIDGE_JAVA11_CONTRACT_PASS: 16 live method cases, mutant rejected, no Minecraft jars')
