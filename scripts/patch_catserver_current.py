#!/usr/bin/env python3
"""Optimizes the exact CatServer source version underpinning CUANTIC live (May 2023).

Upstream LGPL-3.0 1d8d63138be77a606df2a5e940b960065948f983. Original
Bukkit events keep cancellation and setItem semantics; no listeners => skip
wrapper/clone/event allocation. No mod/plugin is removed. STRICT match.
"""
from pathlib import Path
import sys
from patch_catserver_hotpath import once, update_hunk_counts, patch_hopper_push

HOPPER = Path("patches/minecraft/net/minecraft/tileentity/HopperTileEntity.java.patch")
EVENT = Path("src/main/java/org/bukkit/event/inventory/InventoryMoveItemEvent.java")


def patch_old_hopper(text):
    text = patch_hopper_push(text)
    old = """+         // CraftBukkit start - Call event on collection of items from inventories into the hopper
+         CraftItemStack oitemstack = CraftItemStack.asCraftMirror(p_174915_1_.func_70298_a(p_174915_2_, p_174915_0_.func_145831_w().spigotConfig.hopperAmount)); // Spigot
+         Inventory sourceInventory;
+         // Have to special case large chests as they work oddly
+         if (p_174915_1_ instanceof DoubleSidedInventory) {
+            sourceInventory = new org.bukkit.craftbukkit.v1_16_R3.inventory.CraftInventoryDoubleChest((DoubleSidedInventory) p_174915_1_);
+         } else {
+            sourceInventory = CatInventoryUtils.getOwner(p_174915_1_).getInventory();
+         }
+
+         InventoryHolder owner = CatInventoryUtils.getOwner(p_174915_0_);
+         Inventory hopperOwner = (owner != null ? owner.getInventory() : new CatCustomInventory(p_174915_0_).getInventory());
+
+         InventoryMoveItemEvent event = new InventoryMoveItemEvent(sourceInventory, oitemstack.clone(), hopperOwner, false);
+         p_174915_0_.func_145831_w().getCBServer().getPluginManager().callEvent(event);
+         if (event.isCancelled()) {
+            p_174915_1_.func_70299_a(p_174915_2_, itemstack1);
+            if (p_174915_0_ instanceof HopperTileEntity) {
+               ((HopperTileEntity) p_174915_0_).func_145896_c(p_174915_0_.func_145831_w().spigotConfig.hopperTransfer); // Spigot
+            } else if (p_174915_0_ instanceof HopperMinecartEntity) {
+               ((HopperMinecartEntity) p_174915_0_).func_98042_n(p_174915_0_.func_145831_w().spigotConfig.hopperTransfer / 2); // Spigot
+            }
+            return false;
+         }
+         int origCount = event.getItem().getAmount(); // Spigot
+         ItemStack itemstack2 = func_174918_a(p_174915_1_, p_174915_0_, CraftItemStack.asNMSCopy(event.getItem()), null);
+         // CraftBukkit end"""
    new = """+         // CUANTIC: vanilla transfer fast path only when zero Bukkit listeners.
+         ItemStack moved = p_174915_1_.func_70298_a(p_174915_2_, p_174915_0_.func_145831_w().spigotConfig.hopperAmount);
+         int origCount;
+         ItemStack itemstack2;
+         if (InventoryMoveItemEvent.getHandlerList().getRegisteredListeners().length == 0) {
+            origCount = moved.func_190916_E();
+            itemstack2 = func_174918_a(p_174915_1_, p_174915_0_, moved, null);
+         } else {
+            CraftItemStack oitemstack = CraftItemStack.asCraftMirror(moved);
+            Inventory sourceInventory;
+            if (p_174915_1_ instanceof DoubleSidedInventory) {
+               sourceInventory = new org.bukkit.craftbukkit.v1_16_R3.inventory.CraftInventoryDoubleChest((DoubleSidedInventory) p_174915_1_);
+            } else {
+               sourceInventory = CatInventoryUtils.getOwner(p_174915_1_).getInventory();
+            }
+            InventoryHolder owner = CatInventoryUtils.getOwner(p_174915_0_);
+            Inventory hopperOwner = (owner != null ? owner.getInventory() : new CatCustomInventory(p_174915_0_).getInventory());
+            InventoryMoveItemEvent event = new InventoryMoveItemEvent(sourceInventory, oitemstack.clone(), hopperOwner, false);
+            p_174915_0_.func_145831_w().getCBServer().getPluginManager().callEvent(event);
+            if (event.isCancelled()) {
+               p_174915_1_.func_70299_a(p_174915_2_, itemstack1);
+               if (p_174915_0_ instanceof HopperTileEntity) {
+                  ((HopperTileEntity) p_174915_0_).func_145896_c(p_174915_0_.func_145831_w().spigotConfig.hopperTransfer);
+               } else if (p_174915_0_ instanceof HopperMinecartEntity) {
+                  ((HopperMinecartEntity) p_174915_0_).func_98042_n(p_174915_0_.func_145831_w().spigotConfig.hopperTransfer / 2);
+               }
+               return false;
+            }
+            origCount = event.getRawItem().getAmount();
+            itemstack2 = func_174918_a(p_174915_1_, p_174915_0_, CraftItemStack.asNMSCopy(event.getRawItem()), null);
+         }"""
    text = once(text, old, new)
    text = once(text, """+      // CraftBukkit start
+      InventoryHolder owner = CatInventoryUtils.getOwner(p_200114_0_);
+      Inventory sourceInventory = owner != null ? owner.getInventory() : new CatCustomInventory(p_200114_0_).getInventory();
+      InventoryPickupItemEvent event = new InventoryPickupItemEvent(sourceInventory, (org.bukkit.entity.Item) p_200114_1_.getBukkitEntity());
+      p_200114_1_.field_70170_p.getCBServer().getPluginManager().callEvent(event);
+      if (event.isCancelled()) {
+         return false;
+      }
+      // CraftBukkit end""", """+      // CUANTIC: allocate pickup wrapper only if a plugin listens.
+      if (InventoryPickupItemEvent.getHandlerList().getRegisteredListeners().length != 0) {
+         InventoryHolder owner = CatInventoryUtils.getOwner(p_200114_0_);
+         Inventory sourceInventory = owner != null ? owner.getInventory() : new CatCustomInventory(p_200114_0_).getInventory();
+         InventoryPickupItemEvent event = new InventoryPickupItemEvent(sourceInventory, (org.bukkit.entity.Item) p_200114_1_.getBukkitEntity());
+         p_200114_1_.field_70170_p.getCBServer().getPluginManager().callEvent(event);
+         if (event.isCancelled()) return false;
+      }""")
    return update_hunk_counts(text)


def patch_event(text):
    if "getRawItem()" in text:
        raise ValueError("Old CatServer unexpectedly already has getRawItem()")
    return once(text, """    public static HandlerList getHandlerList() {
        return handlers;
    }
}""", """    public static HandlerList getHandlerList() {
        return handlers;
    }

    // CUANTIC: internal read only after synchronous listeners complete. The public
    // Bukkit getItem() still returns a defensive clone for plugins, unchanged.
    public ItemStack getRawItem() {
        return this.itemStack;
    }
}""")


def main(root):
    hopper, event = root / HOPPER, root / EVENT
    h, e = patch_old_hopper(hopper.read_text()), patch_event(event.read_text())
    hopper.write_text(h)
    event.write_text(e)
    print("Patched CURRENT CatServer 1d8d6313 source: hopper hot path + Bukkit event clone elimination")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: patch_catserver_current.py <pinned CatServer 1d8d6313 source tree>")
    main(Path(sys.argv[1]))
