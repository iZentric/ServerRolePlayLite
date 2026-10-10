package org.bukkit.plugin.java;
import org.bukkit.Server;
import org.bukkit.plugin.Plugin;
import org.bukkit.plugin.PluginDescriptionFile;
public abstract class JavaPlugin implements Plugin {
    public final Server getServer() { throw new Error("stub"); }
    public final PluginDescriptionFile getDescription() { throw new Error("stub"); }
    public void onEnable() {}
    public void onDisable() {}
}
