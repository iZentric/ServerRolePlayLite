package org.bukkit.event.player;
import org.bukkit.entity.Player;
import org.bukkit.event.Cancellable;
import org.bukkit.event.Event;
public class PlayerCommandPreprocessEvent extends Event implements Cancellable {
    public String getMessage() { throw new Error("stub"); }
    public void setMessage(String message) {}
    public Player getPlayer() { throw new Error("stub"); }
    public boolean isCancelled() { return false; }
    public void setCancelled(boolean cancel) {}
}
