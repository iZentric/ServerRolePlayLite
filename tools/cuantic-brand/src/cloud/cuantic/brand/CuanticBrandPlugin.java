package cloud.cuantic.brand;

import org.bukkit.Bukkit;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerCommandPreprocessEvent;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Cuantic — brand pentru /version.
 *
 * Nu furam meritul upstream-ului: Comanda /version a lui Bukkit ramane functionala pentru
 * orice plugin care o apela programatic, iar noi doar inlocuim textul vazut de jucator,
 * pastrand sirul original al upstream-ului pe a doua linie (CERINTA: provenienta vizibila).
 */
public class CuanticBrandPlugin extends JavaPlugin implements Listener {

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getServer().getConsoleSender().sendMessage(
            "\u00A7b\u00A7lCuantic \u00A7f" + cuantic() + " \u00A77(Minecraft " + Bukkit.getMinecraftVersion()
            + ", API " + Bukkit.getBukkitVersion() + ") \u00A7a— hibrid invizibil, cost 0");
    }

    private static String curata(String t) {
        return t.replaceAll("\u00A7.", "");
    }

    private String cuantic() {
        String v = getDescription().getVersion();
        return (v == null || v.isEmpty()) ? "?" : v;
    }

    @EventHandler(ignoreCancelled = true)
    public void onCommand(PlayerCommandPreprocessEvent e) {
        String m = e.getMessage().toLowerCase();
        // Aliasurile reale ale comenzii /version din Bukkit: version, about, ver (+ /cuantic).
        // FARA poarta de permisiune: inainte, un jucator care nu e OP primea textul vanilla
        // pentru ca skill-ul nostru se dadea la o parte din teama de a incurca API-ul.
        if (!m.equals("/version") && !m.equals("/ver") && !m.equals("/about")
                && !m.equals("/bukkit:version") && !m.equals("/bukkit:ver") && !m.equals("/bukkit:about")
                && !m.startsWith("/cuantic")) return;
        e.setCancelled(true);
        String sender = e.getPlayer().getName();
        String l1 = "\u00A76\u00A7l\u00BB \u00A7b\u00A7lCuantic \u00A7f" + cuantic()
            + " \u00A77(build propriu, Java " + System.getProperty("java.version") + ")";
        String l2 = "\u00A77Minecraft \u00A7f" + Bukkit.getMinecraftVersion()
            + " \u00A77· API \u00A7f" + Bukkit.getBukkitVersion() + " \u00A77· motor \u00A7f" + Bukkit.getName();
        String l3 = "\u00A77Cuantic based on / adapted from: \u00A7f" + Bukkit.getVersion();
        e.getPlayer().sendMessage(l1);
        e.getPlayer().sendMessage(l2);
        e.getPlayer().sendMessage(l3);
        // Aceleasi 3 linii in log (fara coduri de culoare), ca testul T10 sa aiba dovada
        // in live.log ca provineenta a fost afisata, nu doar ca brandul a aparut.
        getServer().getConsoleSender().sendMessage("[Cuantic/version] " + sender + ": "
            + curata(l1) + " | " + curata(l2) + " | " + curata(l3));
    }
}
