package cloud.cuantic.brand;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import org.bukkit.Bukkit;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerCommandPreprocessEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.server.ServerCommandEvent;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Cuantic — motor & brand pentru /version, consola, OP garantat pt proprietar si tuning runtime
 * (stil DivineMC).
 *
 * 1) Foloseste exclusiv semnaturile reale din Bukkit 1.16.5 (CommandSender, ConsoleCommandSender,
 *    Bukkit.getVersion(), Bukkit.getBukkitVersion(), Bukkit.getName(), Bukkit.getLogger()).
 * 2) Asculta ATAT jucatorii (PlayerCommandPreprocessEvent, fara verificare de OP) CAT SI
 *    consola serverului (ServerCommandEvent + /cuantic), ca testul automat T10 din
 *    acceptance.sh si orice jucator sa primeasca raspunsul Cuantic + provenienta upstream.
 * 3) Activeaza la pornire prin reflectie campurile lasate pe // TODO in CatServerConfig
 *    (enableSkipEntityTick, enableSkipTileEntityTick, maxEntityCollision=4, worldGenMaxTickTime=10).
 * 4) Acorda automat OP + LuckPerms (*) proprietarului (iZentric) la intrarea pe server sau la
 *    orice comanda, fara sa mai depinda de puntea FIFO din consola.
 */
public class CuanticBrandPlugin extends JavaPlugin implements Listener {

    private static final String OWNER_NAME = "iZentric";

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        String tune = applyRuntimeEngineTuning();
        Bukkit.getLogger().info(
            "[Cuantic] Motor hibrid activ: Cuantic " + cuantic()
            + " (MC 1.16.5, API " + Bukkit.getBukkitVersion()
            + ", motor " + Bukkit.getName() + ") | based on: " + Bukkit.getVersion()
            + " | runtime-tech: " + tune);
    }

    private String applyRuntimeEngineTuning() {
        StringBuilder sb = new StringBuilder();
        try {
            Class<?> catCls = Class.forName("catserver.server.CatServer");
            Method getCfg = catCls.getMethod("getConfig");
            Object cfg = getCfg.invoke(null);
            if (cfg != null) {
                setField(cfg, "keepSpawnInMemory", Boolean.FALSE, sb);
                setField(cfg, "enableSkipEntityTick", Boolean.TRUE, sb);
                setField(cfg, "enableSkipTileEntityTick", Boolean.TRUE, sb);
                setField(cfg, "maxEntityCollision", Integer.valueOf(2), sb);
                setField(cfg, "worldGenMaxTickTime", Integer.valueOf(8), sb);
                setField(cfg, "disableFMLStatusModInfo", Boolean.TRUE, sb);
                setField(cfg, "enableDynmapCompatible", Boolean.FALSE, sb);
                setField(cfg, "enableMythicMobsPatcherCompatible", Boolean.FALSE, sb);
                setField(cfg, "defaultInstallPluginSpark", Boolean.FALSE, sb);
                setField(cfg, "versionCheck", Boolean.FALSE, sb);
                setField(cfg, "forceSaveOnWatchdog", Boolean.TRUE, sb);
                try {
                    Field fHop = cfg.getClass().getDeclaredField("disableHopperMoveEventWorlds");
                    fHop.setAccessible(true);
                    @SuppressWarnings("unchecked")
                    java.util.List<String> hop = (java.util.List<String>) fHop.get(cfg);
                    if (hop != null) {
                        hop.clear();
                        hop.add("world");
                        hop.add("DIM-1");
                        hop.add("DIM1");
                        sb.append(", noHopperEvent=3w");
                    }
                    Field fDim = cfg.getClass().getDeclaredField("autoUnloadDimensions");
                    fDim.setAccessible(true);
                    @SuppressWarnings("unchecked")
                    java.util.List<Integer> dims = (java.util.List<Integer>) fDim.get(cfg);
                    if (dims != null) {
                        dims.clear();
                        dims.add(Integer.valueOf(-1));
                        dims.add(Integer.valueOf(1));
                        sb.append(", autoUnloadDims=[-1,1]");
                    }
                } catch (Throwable ignored) {}
            }
        } catch (Throwable ignored) {
            // Pe Arclight / Mist nu exista clasa CatServer; ignora in liniste
        }
        // Stratul 2: SpigotConfig (Gale/Pufferfish/Purpur runtime tuning + anti-rubberband vehicule)
        try {
            Class<?> spg = Class.forName("org.spigotmc.SpigotConfig");
            setStaticField(spg, "disableStatSaving", Boolean.TRUE, sb);
            setStaticField(spg, "saveUserCacheOnStopOnly", Boolean.TRUE, sb);
            setStaticField(spg, "logVillagerDeaths", Boolean.FALSE, sb);
            setStaticField(spg, "movedWronglyThreshold", Double.valueOf(0.35D), sb);
            setStaticField(spg, "movedTooQuicklyMultiplier", Double.valueOf(25.0D), sb);
        } catch (Throwable ignored) {}
        return sb.length() > 0 ? sb.toString() : "standard";
    }

    private static void setStaticField(Class<?> cls, String name, Object val, StringBuilder sb) {
        try {
            Field f = cls.getDeclaredField(name);
            f.setAccessible(true);
            f.set(null, val);
            if (sb.length() > 0) sb.append(", ");
            sb.append(name).append("=").append(val);
        } catch (Throwable ignored) {}
    }

    private static void setField(Object target, String name, Object val, StringBuilder sb) {
        try {
            Field f = target.getClass().getDeclaredField(name);
            f.setAccessible(true);
            f.set(target, val);
            if (sb.length() > 0) sb.append(", ");
            sb.append(name).append("=").append(val);
        } catch (Throwable ignored) {}
    }

    private void ensureOwnerOp(Player p) {
        if (p == null) return;
        String name = p.getName();
        if (name == null || !name.equalsIgnoreCase(OWNER_NAME)) return;
        try {
            if (!p.isOp()) {
                p.setOp(true);
                Bukkit.getLogger().info("[Cuantic/OP] Operator acordat automat pentru " + name);
                try {
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "lp user " + name + " permission set * true");
                } catch (Throwable ignored) {}
            }
        } catch (Throwable ignored) {}
    }

    private static String curata(String t) {
        return t.replaceAll("\u00A7.", "");
    }

    private String cuantic() {
        String v = getDescription().getVersion();
        return (v == null || v.isEmpty()) ? "?" : v;
    }

    private static boolean esteComandaVersiune(String raw) {
        if (raw == null) return false;
        String m = raw.trim().toLowerCase();
        if (m.startsWith("/")) m = m.substring(1);
        int sp = m.indexOf(' ');
        String cmd = (sp >= 0) ? m.substring(0, sp) : m;
        return cmd.equals("version") || cmd.equals("ver") || cmd.equals("about")
            || cmd.equals("bukkit:version") || cmd.equals("bukkit:ver") || cmd.equals("bukkit:about")
            || cmd.equals("cuantic") || cmd.equals("cver") || cmd.equals("cuantic-brand:cuantic");
    }

    private void raspunde(CommandSender dest, String senderName) {
        String l1 = "\u00A76\u00A7l\u00BB \u00A7b\u00A7lCuantic \u00A7f" + cuantic()
            + " \u00A77(build propriu, Java " + System.getProperty("java.version") + ")";
        String l2 = "\u00A77Minecraft \u00A7f1.16.5 \u00A77\u00B7 API \u00A7f"
            + Bukkit.getBukkitVersion() + " \u00A77\u00B7 motor \u00A7f" + Bukkit.getName();
        String l3 = "\u00A77Cuantic based on / adapted from: \u00A7f" + Bukkit.getVersion();
        if (dest != null) {
            dest.sendMessage(l1);
            dest.sendMessage(l2);
            dest.sendMessage(l3);
        }
        Bukkit.getLogger().info("[Cuantic/version] " + senderName + ": "
            + curata(l1) + " | " + curata(l2) + " | " + curata(l3));
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent e) {
        ensureOwnerOp(e.getPlayer());
    }

    @EventHandler
    public void onPlayerCommand(PlayerCommandPreprocessEvent e) {
        ensureOwnerOp(e.getPlayer());
        if (e.isCancelled()) return;
        if (!esteComandaVersiune(e.getMessage())) return;
        e.setCancelled(true);
        raspunde(e.getPlayer(), e.getPlayer().getName());
    }

    @EventHandler
    public void onServerCommand(ServerCommandEvent e) {
        if (e.isCancelled()) return;
        if (!esteComandaVersiune(e.getCommand())) return;
        e.setCancelled(true);
        raspunde(e.getSender(), "CONSOLE");
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (sender instanceof Player) {
            ensureOwnerOp((Player) sender);
        }
        raspunde(sender, sender != null ? sender.getName() : "CONSOLE");
        return true;
    }
}
