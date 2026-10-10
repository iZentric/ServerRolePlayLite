package org.bukkit;

import java.util.logging.Logger;
import org.bukkit.command.ConsoleCommandSender;
import org.bukkit.plugin.PluginManager;

public interface Server {
    PluginManager getPluginManager();
    ConsoleCommandSender getConsoleSender();
    Logger getLogger();
    String getName();
    String getVersion();
    String getBukkitVersion();
}
