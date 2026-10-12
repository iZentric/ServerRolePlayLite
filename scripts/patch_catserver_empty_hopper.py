#!/usr/bin/env python3
"""Small, behavior-preserving fast path on exact CatServer 1d8d6313 source.

Push-out on an EMPTY hopper cannot transfer an item. Avoid discovering its
neighbour, resolving Forge capabilities and allocating inventory wrappers.
The pull-in path remains untouched and can still fill that empty hopper.
LGPL-3.0 base: Luohuayu/CatServer commit 1d8d63138be77a606df2a5e940b960065948f983.
"""
from pathlib import Path
import sys
from patch_catserver_hotpath import once, update_hunk_counts

PATCH = Path("patches/minecraft/net/minecraft/tileentity/HopperTileEntity.java.patch")


def patch(src):
    old = """    private boolean func_145883_k() {
+      if (net.minecraftforge.items.VanillaInventoryCodeHooks.insertHook(this)) return true;
       IInventory iinventory = this.func_145895_l();"""
    new = """    private boolean func_145883_k() {
+      // CUANTIC: this method pushes OUT only. Empty inventory cannot push;
+      // the independent pull path still runs, with all Forge/Bukkit events intact.
+      boolean hasItems = false;
+      for (int slot = 0; slot < this.func_70302_i_(); slot++) {
+         if (!this.func_70301_a(slot).func_190926_b()) {
+            hasItems = true;
+            break;
+         }
+      }
+      if (!hasItems) return false;
+      if (net.minecraftforge.items.VanillaInventoryCodeHooks.insertHook(this)) return true;
       IInventory iinventory = this.func_145895_l();"""
    return update_hunk_counts(once(src, old, new))


def main(root):
    file = root / PATCH
    file.write_text(patch(file.read_text()))
    print("Patched EMPTY hopper push short circuit; Forge capability and pull paths untouched")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: patch_catserver_empty_hopper.py <pinned CatServer source tree>")
    main(Path(sys.argv[1]))
