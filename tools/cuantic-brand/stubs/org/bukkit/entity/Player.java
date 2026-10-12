package org.bukkit.entity;

import org.bukkit.command.CommandSender;

public interface Player extends CommandSender {
    String getName();
    boolean hasPermission(String name);
    boolean isOp();
    void setOp(boolean value);
}
