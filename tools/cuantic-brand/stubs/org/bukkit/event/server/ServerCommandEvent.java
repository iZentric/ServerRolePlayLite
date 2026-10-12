package org.bukkit.event.server;

import org.bukkit.command.CommandSender;
import org.bukkit.event.Cancellable;
import org.bukkit.event.Event;

public class ServerCommandEvent extends Event implements Cancellable {
    public String getCommand() { throw new Error("stub"); }
    public void setCommand(String message) {}
    public CommandSender getSender() { throw new Error("stub"); }
    public boolean isCancelled() { return false; }
    public void setCancelled(boolean cancel) {}
}
