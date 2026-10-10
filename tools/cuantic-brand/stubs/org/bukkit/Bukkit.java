package org.bukkit;

import java.util.logging.Logger;
import org.bukkit.command.CommandSender;
import org.bukkit.command.ConsoleCommandSender;
import org.bukkit.plugin.PluginManager;

public final class Bukkit {
    public static Server getServer() { throw new Error("stub"); }
    public static String getName() { throw new Error("stub"); }
    public static String getVersion() { throw new Error("stub"); }
    public static String getBukkitVersion() { throw new Error("stub"); }
    public static ConsoleCommandSender getConsoleSender() { throw new Error("stub"); }
    public static Logger getLogger() { throw new Error("stub"); }
    public static PluginManager getPluginManager() { throw new Error("stub"); }
    public static boolean dispatchCommand(CommandSender sender, String commandLine) { throw new Error("stub"); }
}
