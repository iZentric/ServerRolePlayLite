package org.bukkit.entity;
import org.bukkit.MessageSender;
public interface Player extends MessageSender {
    String getName();
    boolean hasPermission(String name);
}
