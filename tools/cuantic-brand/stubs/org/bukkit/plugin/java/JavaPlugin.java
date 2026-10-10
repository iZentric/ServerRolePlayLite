package org.bukkit.plugin.java;

import java.util.logging.Logger;
import org.bukkit.Server;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.plugin.Plugin;
import org.bukkit.plugin.PluginDescriptionFile;

public abstract class JavaPlugin implements Plugin {
    public final Server getServer() { throw new Error("stub"); }
    public final PluginDescriptionFile getDescription() { throw new Error("stub"); }
    public Logger getLogger() { throw new Error("stub"); }
    public void onEnable() {}
    public void onDisable() {}
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) { return false; }
}
