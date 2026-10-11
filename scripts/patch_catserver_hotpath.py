#!/usr/bin/env python3
"""Patch pinned upstream CatServer 1.16.5 hot path BEFORE `gradlew setup`.

Strict matches fail closed if upstream changes. Keep Forge/Bukkit mod/plugin semantics:
- no event listeners -> no Bukkit InventoryMoveItemEvent or wrapper allocations;
- listeners present -> fire synchronously, honor cancellation and setItem exactly as before;
- use upstream CatServer's getRawItem() AFTER listeners instead of cloning twice;
- fix null dereference of event when inventory has no Bukkit owner.
LGPL-3.0 upstream: https://github.com/Luohuayu/CatServer/tree/1.16.5
"""
from pathlib import Path
import re
import sys

HOPPER = Path("patches/minecraft/net/minecraft/tileentity/HopperTileEntity.java.patch")
HOOKS = Path("src/main/java/net/minecraftforge/items/VanillaInventoryCodeHooks.java")


def once(text, old, new):
    n = text.count(old)
    if n != 1:
        raise ValueError(f"Expected exactly one upstream match, got {n}: {old[:120]!r}")
    return text.replace(old, new, 1)


def update_hunk_counts(text):
    headers = list(re.finditer(r"^@@ (-\d+(?:,\d+)? \+_),(\d+)( @@[^\n]*)$", text, re.M))
    if not headers:
        raise ValueError("CatServer source patch has no expected hunk headers")
    for i, match in reversed(list(enumerate(headers))):
        body = text[match.end() + 1:headers[i + 1].start() if i + 1 < len(headers) else len(text)]
        count = sum(line[:1] in ("+", " ") and not line.startswith("+++") for line in body.splitlines())
        text = text[:match.start()] + "@@ " + match.group(1) + "," + str(count) + match.group(3) + text[match.end():]
    return text


def patch_hopper(src):
    old = """+                  // CraftBukkit start - Call event when pushing items into other inventories
+                  CraftItemStack oitemstack = CraftItemStack.asCraftMirror(this.func_70298_a(i, field_145850_b.spigotConfig.hopperAmount)); // Spigot
+                  Inventory destinationInventory;
+                  // Have to special case large chests as they work oddly
+                  if (iinventory instanceof DoubleSidedInventory) {
+                     destinationInventory = new org.bukkit.craftbukkit.v1_16_R3.inventory.CraftInventoryDoubleChest((DoubleSidedInventory) iinventory);
+                  } else {
+                     destinationInventory = CatInventoryUtils.getBukkitInventory(iinventory);
+                  }
+                  InventoryHolder owner = CatInventoryUtils.getOwner((TileEntity) this);
+                  Inventory hopperOwner = (owner != null ? owner.getInventory() : new CatCustomInventory(this).getInventory());
+                  InventoryMoveItemEvent event = new InventoryMoveItemEvent(hopperOwner, oitemstack.clone(), destinationInventory, true);
+                  // LoliServer end
+                  this.func_145831_w().getCBServer().getPluginManager().callEvent(event);
+                  if (event.isCancelled()) {
+                     this.func_70299_a(i, itemstack);
+                     this.func_145896_c(field_145850_b.spigotConfig.hopperTransfer); // Spigot
+                     return false;
+                  }
+                  int origCount = event.getItem().getAmount(); // Spigot
+                  ItemStack itemstack1 = func_174918_a(this, iinventory, CraftItemStack.asNMSCopy(event.getItem()), direction);
+                  // CraftBukkit end"""
    new = """+                  // CUANTIC: no registered Bukkit listeners => vanilla transfer without
+                  // CraftItemStack, Bukkit inventory wrappers or event allocation.
+                  ItemStack itemstack1;
+                  int origCount;
+                  if (InventoryMoveItemEvent.getHandlerList().getRegisteredListeners().length == 0) {
+                     ItemStack moved = this.func_70298_a(i, field_145850_b.spigotConfig.hopperAmount);
+                     origCount = moved.func_190916_E();
+                     itemstack1 = func_174918_a(this, iinventory, moved, direction);
+                  } else {
+                     CraftItemStack oitemstack = CraftItemStack.asCraftMirror(this.func_70298_a(i, field_145850_b.spigotConfig.hopperAmount));
+                     Inventory destinationInventory;
+                     if (iinventory instanceof DoubleSidedInventory) {
+                        destinationInventory = new org.bukkit.craftbukkit.v1_16_R3.inventory.CraftInventoryDoubleChest((DoubleSidedInventory) iinventory);
+                     } else {
+                        destinationInventory = CatInventoryUtils.getBukkitInventory(iinventory);
+                     }
+                     InventoryHolder owner = CatInventoryUtils.getOwner((TileEntity) this);
+                     Inventory hopperOwner = (owner != null ? owner.getInventory() : new CatCustomInventory(this).getInventory());
+                     InventoryMoveItemEvent event = new InventoryMoveItemEvent(hopperOwner, oitemstack.clone(), destinationInventory, true);
+                     this.func_145831_w().getCBServer().getPluginManager().callEvent(event);
+                     if (event.isCancelled()) {
+                        this.func_70299_a(i, itemstack);
+                        this.func_145896_c(field_145850_b.spigotConfig.hopperTransfer);
+                        return false;
+                     }
+                     // CatServer getRawItem() returns the post-listener item; unlike getItem(),
+                     // it does not clone twice. setItem()/cancellation remain respected.
+                     origCount = event.getRawItem().getAmount();
+                     itemstack1 = func_174918_a(this, iinventory, CraftItemStack.asNMSCopy(event.getRawItem()), direction);
+                  }"""
    src = once(src, old, new)
    src = once(src, """+         InventoryHolder owner = CatInventoryUtils.getOwner(p_174915_0_);
+         Inventory hopperOwner = (owner != null ? owner.getInventory() : new CatCustomInventory(p_174915_0_).getInventory());
+
+         InventoryMoveItemEvent event = null;
+         if (true /*!TileEntityHopper.skipHopperEvents*/) {
+            CraftItemStack oitemstack = CraftItemStack.asCraftMirror(originNMSStack);""", """+         InventoryMoveItemEvent event = null;
+         if (InventoryMoveItemEvent.getHandlerList().getRegisteredListeners().length != 0) {
+            InventoryHolder owner = CatInventoryUtils.getOwner(p_174915_0_);
+            Inventory hopperOwner = (owner != null ? owner.getInventory() : new CatCustomInventory(p_174915_0_).getInventory());
+            CraftItemStack oitemstack = CraftItemStack.asCraftMirror(originNMSStack);""")
    # Upstream dereferenced event outside the destinationInventory != null branch.
    src = once(src, "+            if (event.isCallSetItem) resultNMSStack = CraftItemStack.asNMSCopy(event.getRawItem());", "+            if (event != null && event.isCallSetItem) resultNMSStack = CraftItemStack.asNMSCopy(event.getRawItem());")
    src = once(src, """+      // CraftBukkit start
+      InventoryHolder owner = CatInventoryUtils.getOwner(p_200114_0_);
+      Inventory sourceInventory = owner != null ? owner.getInventory() : new CatCustomInventory(p_200114_0_).getInventory();
+      InventoryPickupItemEvent event = new InventoryPickupItemEvent(sourceInventory, (org.bukkit.entity.Item) p_200114_1_.getBukkitEntity());
+      p_200114_1_.field_70170_p.getCBServer().getPluginManager().callEvent(event);
+      if (event.isCancelled()) {
+         return false;
+      }
+      // CraftBukkit end""", """+      // CUANTIC: skip allocation when no plugin listens; still fire for listeners.
+      if (InventoryPickupItemEvent.getHandlerList().getRegisteredListeners().length != 0) {
+         InventoryHolder owner = CatInventoryUtils.getOwner(p_200114_0_);
+         Inventory sourceInventory = owner != null ? owner.getInventory() : new CatCustomInventory(p_200114_0_).getInventory();
+         InventoryPickupItemEvent event = new InventoryPickupItemEvent(sourceInventory, (org.bukkit.entity.Item) p_200114_1_.getBukkitEntity());
+         p_200114_1_.field_70170_p.getCBServer().getPluginManager().callEvent(event);
+         if (event.isCancelled()) return false;
+      }""")
    return update_hunk_counts(src)


def patch_hooks(src):
    src = once(src, """                    org.bukkit.craftbukkit.v1_16_R3.inventory.CraftItemStack oitemstack = org.bukkit.craftbukkit.v1_16_R3.inventory.CraftItemStack.asCraftMirror(originNMSStack);

                    org.bukkit.inventory.InventoryHolder owner = catserver.server.inventory.CatInventoryUtils.getOwner((TileEntity) destination);
                    org.bukkit.inventory.Inventory destinationInventory = owner != null ? owner.getInventory() : catserver.server.inventory.CatCustomInventory.getInventoryFromForge(itemHandler);

                    if (destinationInventory != null) {""", """                    // CUANTIC: no Bukkit InventoryMoveItemEvent listeners = no wrappers/event.
                    if (org.bukkit.event.inventory.InventoryMoveItemEvent.getHandlerList().getRegisteredListeners().length != 0) {
                        org.bukkit.craftbukkit.v1_16_R3.inventory.CraftItemStack oitemstack = org.bukkit.craftbukkit.v1_16_R3.inventory.CraftItemStack.asCraftMirror(originNMSStack);
                        org.bukkit.inventory.InventoryHolder owner = catserver.server.inventory.CatInventoryUtils.getOwner((TileEntity) destination);
                        org.bukkit.inventory.Inventory destinationInventory = owner != null ? owner.getInventory() : catserver.server.inventory.CatCustomInventory.getInventoryFromForge(itemHandler);
                        if (destinationInventory != null) {""")
    src = once(src, """                        if (event.isCallSetItem) resultNMSStack = org.bukkit.craftbukkit.v1_16_R3.inventory.CraftItemStack.asNMSCopy(event.getRawItem());
                    }

                    ItemStack remainder = putStackInInventoryAllSlots""", """                        if (event.isCallSetItem) resultNMSStack = org.bukkit.craftbukkit.v1_16_R3.inventory.CraftItemStack.asNMSCopy(event.getRawItem());
                        }
                    }

                    ItemStack remainder = putStackInInventoryAllSlots""")
    src = once(src, "if (true /*!TileEntityHopper.skipHopperEvents*/) {", "if (org.bukkit.event.inventory.InventoryMoveItemEvent.getHandlerList().getRegisteredListeners().length != 0) {")
    return src


def main(root):
    hopper, hooks = root / HOPPER, root / HOOKS
    a, b = hopper.read_text(), hooks.read_text()
    patched_a, patched_b = patch_hopper(a), patch_hooks(b)
    # All assertions must have passed before either file is written.
    hopper.write_text(patched_a)
    hooks.write_text(patched_b)
    print("Patched hopper event fast paths, clone removal and null guard (strict upstream match)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: patch_catserver_hotpath.py <pinned CatServer source tree>")
    main(Path(sys.argv[1]))
