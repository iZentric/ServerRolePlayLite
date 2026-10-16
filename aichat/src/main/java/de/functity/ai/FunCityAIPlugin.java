package de.functity.ai;

import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.ConsoleCommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Scanner;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * FunCityAI — agent operational de chat pentru FunCity RP.
 * Principii (mission-locked): lista INCHISA de actiuni; fara RCON; fara shell/cmdlui libere;
 * acte sensibile doar cu confirmare /aiyes; tot ce executa se scrie in audit.log;
 * LLM-ul (optional) doar compune raspunsuri — nu genereaza niciodata comenzi executate.
 */
public class FunCityAIPlugin extends JavaPlugin implements Listener {

    private final Map<UUID, Long> lastUse = new ConcurrentHashMap<>();
    private final Map<String, Pending> pending = new ConcurrentHashMap<>();
    private double tps = 20.0;
    private long windowStart;
    private int windowTicks;
    private BufferedWriter audit;

    private static final Pattern NAME = Pattern.compile("^[A-Za-z0-9_]{1,16}$");
    private static final Pattern NUM = Pattern.compile("^-?\\d{1,9}$");

    private static final class Pending {
        final UUID who; final String what; final long until;
        Pending(UUID who, String what, long until) { this.who = who; this.what = what; this.until = until; }
    }

    @Override
    public void onEnable() {
        saveDefaultConfig();
        getCommand("ai").setExecutor(this::onAi);
        getCommand("aiyes").setExecutor(this::onAiYes);
        Bukkit.getPluginManager().registerEvents(this, this);
        windowStart = System.nanoTime();
        // masurator de TPS: 200 de ticki, apoi cat timp au durat
        Bukkit.getScheduler().runTaskTimer(this, () -> {
            windowTicks += 200;
            long now = System.nanoTime();
            double secs = (now - windowStart) / 1e9;
            if (secs > 0) tps = Math.min(20.0, windowTicks / secs);
            windowTicks = 0; windowStart = now;
        }, 200L, 200L);
        try {
            File d = new File(getDataFolder(), "audit.log");
            audit = new BufferedWriter(new FileWriter(d, true));
        } catch (Exception e) { getLogger().warning("audit indisponibil: " + e.getMessage()); }
        log("plugin enabled");
    }

    @Override
    public void onDisable() { log("plugin disabled"); try { if (audit != null) audit.close(); } catch (Exception ignored) {} }

    private boolean onAi(CommandSender s, Command c, String label, String[] a) {
        if (!(s instanceof Player)) { s.sendMessage("Doar din joc."); return true; }
        Player p = (Player) s;
        if (!throttled(p)) return true;
        String verb = a.length == 0 ? "help" : a[0].toLowerCase(Locale.ROOT);
        String rest = a.length > 1 ? join(a, 1) : "";
        try {
            switch (verb) {
                case "help": p.sendMessage(ChatColor.AQUA + "/ai status|where <juc>|announce <text>|time <day|night|add N>|weather <clear|rain|storm>" +
                        "\n/admin: /ai kick <juc> <motiv>|whitelist <add|remove> <juc>|ask <intrebare>"); break;
                case "status": p.sendMessage(ChatColor.GREEN + "FunCity RP | jucatori: " + Bukkit.getOnlinePlayers().size() + "/" + Bukkit.getMaxPlayers()
                        + " | TPS " + String.format(Locale.ROOT, "%.1f", tps) + " | RAM " + usedMb() + "/" + maxMb() + "MB"); break;
                case "where": {
                    Player t = Bukkit.getPlayerExact(rest);
                    if (t == null) p.sendMessage("Nu-l vad online pe " + rest);
                    else p.sendMessage(ChatColor.YELLOW + t.getName() + " → world " + t.getWorld().getName()
                            + String.format(Locale.ROOT, " la %d, %d, %d", t.getLocation().getBlockX(), t.getLocation().getBlockY(), t.getLocation().getBlockZ()));
                    break;
                }
                case "follow": {
                    Player t = Bukkit.getPlayerExact(rest);
                    if (t == null) p.sendMessage("Nu-l vad online.");
                    else { p.teleport(t.getLocation()); say("FunCityAI: " + p.getName() + " a ajuns la " + t.getName()); log("follow " + p.getName() + "->" + t.getName()); }
                    break;
                }
                case "announce": if (needAdmin(p, rest)) { say("§b" + rest); log("announce: " + rest); } break;
                case "time": {
                    World w = p.getWorld();
                    if (rest.equalsIgnoreCase("day")) w.setTime(1000);
                    else if (rest.equalsIgnoreCase("night")) w.setTime(13000);
                    else if (rest.equalsIgnoreCase("noon")) w.setTime(6000);
                    else if (rest.equalsIgnoreCase("midnight")) w.setTime(18000);
                    else if (NUM.matcher(rest.replace("add ", "").trim()).matches()) w.setFullTime(w.getFullTime() + Long.parseLong(rest.replace("add ", "").trim()));
                    else { p.sendMessage("time: day|night|noon|midnight|add <t>"); break; }
                    say("FunCityAI: timpul schimbat de " + p.getName()); log("time " + rest + " de " + p.getName()); break;
                }
                case "weather": {
                    World w = p.getWorld();
                    if (rest.equalsIgnoreCase("clear")) { w.setStorm(false); w.setThundering(false); }
                    else if (rest.equalsIgnoreCase("rain")) { w.setStorm(true); w.setThundering(false); }
                    else if (rest.equalsIgnoreCase("storm")) { w.setStorm(true); w.setThundering(true); }
                    else { p.sendMessage("weather: clear|rain|storm"); break; }
                    say("FunCityAI: vremea pusa " + rest + " de " + p.getName()); log("weather " + rest); break;
                }
                case "kick": {
                    if (!canAdmin(p)) return true;
                    String[] pr = rest.split("\\s+", 2);
                    if (pr.length < 1 || !NAME.matcher(pr[0]).matches()) { p.sendMessage("kick <jucator> <motiv>"); break; }
                    ask(p, "kick " + rest);
                    break;
                }
                case "whitelist": {
                    if (!canAdmin(p)) return true;
                    String[] pr = rest.split("\\s+", 2);
                    if (pr.length < 2 || !pr[0].matches("add|remove") || !NAME.matcher(pr[1]).matches()) { p.sendMessage("whitelist add|remove <jucator>"); break; }
                    ask(p, "whitelist " + rest);
                    break;
                }
                case "ask": askLlm(p, rest); break;
                default: p.sendMessage("N-am asta. /ai help"); break;
            }
        } catch (Exception e) {
            p.sendMessage(ChatColor.RED + "A picat comanda: " + e.getClass().getSimpleName());
            log("EROARE /ai " + verb + ": " + e);
        }
        return true;
    }

    private boolean onAiYes(CommandSender s, Command c, String label, String[] a) {
        if (!(s instanceof Player) || a.length == 0) return true;
        Player p = (Player) s;
        if (!canAdmin(p)) return true;
        Pending pd = pending.remove(a[0]);
        if (pd == null || !pd.who.equals(p.getUniqueId()) || System.currentTimeMillis() > pd.until) { p.sendMessage("Fara confirmare in asteptare pentru id-ul ala."); return true; }
        ConsoleCommandSender con = Bukkit.getConsoleSender();
        if (pd.what.startsWith("kick ")) {
            String[] pr = pd.what.substring(5).split("\\s+", 2);
            Player t = Bukkit.getPlayerExact(pr[0]);
            if (t != null) { t.kickPlayer(ChatColor.RED + "[FunCityAI] " + (pr.length > 1 ? pr[1] : "konform /ai")); log("KICK " + pr[0] + " de " + p.getName()); say("§cFunCityAI: " + pr[0] + " a fost dat afara."); }
            else p.sendMessage("Nu e online.");
        } else if (pd.what.startsWith("whitelist ")) {
            Bukkit.dispatchCommand(con, pd.what);
            log("WHITELIST exec: " + pd.what + " (prin " + p.getName() + ")");
            p.sendMessage(ChatColor.GREEN + "Albă lista actualizată (vezi consola).");
        }
        return true;
    }

    // ---- helperi ----
    private boolean needAdmin(Player p, String msg) { if (msg == null || msg.trim().isEmpty()) { p.sendMessage("Textul gol?"); return false; } return true; }
    private boolean canAdmin(Player p) { return p.hasPermission("functityai.admin") || cfgAdmin(p.getUniqueId()); }
    private boolean cfgAdmin(UUID u) { for (String x : getConfig().getStringList("admin_uuids")) if (x.replace("-", "").equalsIgnoreCase(u.toString().replace("-", ""))) return true; return false; }
    private boolean throttled(Player p) {
        long now = System.currentTimeMillis();
        long last = lastUse.getOrDefault(p.getUniqueId(), 0L);
        long lim = getConfig().getLong("rate_limit_ms", 1500);
        if (now - last < lim) { p.sendMessage(ChatColor.GRAY + "Line... te vad."); return true; }
        lastUse.put(p.getUniqueId(), now); return false;
    }
    private String join(String[] a, int from) { StringBuilder sb = new StringBuilder(); for (int i = from; i < a.length; i++) { if (i > from) sb.append(' '); sb.append(a[i]); } return sb.toString().replaceAll("[§\\u00A7]", ""); }
    private void say(String m) { Bukkit.broadcastMessage(m); if (getConfig().getBoolean("echo_in_console", true)) Bukkit.getConsoleSender().sendMessage(m); }
    private String usedMb() { return String.valueOf((Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()) / 1048576); }
    private String maxMb() { return String.valueOf(Runtime.getRuntime().maxMemory() / 1048576); }
    private void ask(Player p, String what) {
        String id = UUID.randomUUID().toString().substring(0, 4);
        pending.put(id, new Pending(p.getUniqueId(), what, System.currentTimeMillis() + 60000));
        p.sendMessage(ChatColor.YELLOW + "Sensibil: „" + what + "”. Confirmă: /aiyes " + id + " (60s)");
        log("ask confirm: " + what + " (id " + id + ", " + p.getName() + ")");
    }
    private synchronized void log(String line) {
        if (audit == null) return;
        try { audit.write("[" + new java.util.Date() + "] " + line); audit.newLine(); audit.flush(); } catch (Exception ignored) {}
    }

    /** LLM = doar text inapoi, in chat. Nimic din raspuns nu devine comanda. */
    private void askLlm(Player p, String question) {
        String ep = getConfig().getString("ai.endpoint", "");
        if (ep.isEmpty()) { p.sendMessage(ChatColor.GRAY + "Mod AI neativat (config aichat/config.yml). Restul lui /ai merge fara AI."); return; }
        if (question.isEmpty()) { p.sendMessage("Intreaba ceva: /ai ask <text>"); return; }
        String q = question.length() > getConfig().getInt("ai.max_input_chars", 400) ? question.substring(0, 400) : question;
        String key = getConfig().getString("ai.api_key", "");
        if (key.isEmpty()) key = System.getenv().getOrDefault("FUNCITYAI_KEY", "");
        final String body = "{\"model\":\"" + esc(getConfig().getString("ai.model", "gpt-4o-mini")) + "\",\"messages\":[{\"role\":\"system\",\"content\":\"Esti FunCityAI, asistentul unui server de roleplay Minecraft. Raspunsuri scurte (max 3 fraze), in limba jucatorului. Nu inventa comenzi si nu cere date." + "\"},{\"role\":\"user\",\"content\":\"" + esc(q) + "\"}],\"max_tokens\":220,\"temperature\":0.4}";
        final String finKey = key;
        Bukkit.getScheduler().runTaskAsynchronously(this, () -> {
            try {
                HttpURLConnection h = (HttpURLConnection) new URL(ep).openConnection();
                h.setConnectTimeout(8000); h.setReadTimeout(getConfig().getInt("ai.timeout_ms", 15000));
                h.setRequestMethod("POST"); h.setDoOutput(true);
                h.setRequestProperty("Content-Type", "application/json");
                if (!finKey.isEmpty()) h.setRequestProperty("Authorization", "Bearer " + finKey);
                try (OutputStream os = h.getOutputStream()) { os.write(body.getBytes(StandardCharsets.UTF_8)); }
                int code = h.getResponseCode();
                InputStream is = code < 400 ? h.getInputStream() : h.getErrorStream();
                String resp = new Scanner(is, "UTF-8").useDelimiter("\\A").next();
                if (code >= 400) { p.sendMessage(ChatColor.RED + "AI a dat " + code + " — nu e treaba mea."); log("ai http " + code); return; }
                Matcher m = Pattern.compile("\"content\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"").matcher(resp);
                if (m.find()) {
                    String text = m.group(1).replace("\\n", "\n").replace("\\\"", "\"").replace("\\/", "/");
                    final String clean = text.length() > 700 ? text.substring(0, 700) : text;
                    Bukkit.getScheduler().runTask(this, () -> {
                        for (String line : clean.split("\\R", 6)) p.sendMessage(ChatColor.AQUA + "[FunCityAI] " + ChatColor.WHITE + line);
                        log("ask('" + q + "') -> ok");
                    });
                } else { p.sendMessage("N-am inteles raspunsul AI-ului."); log("ai parse fail"); }
            } catch (Exception ex) { p.sendMessage(ChatColor.RED + "AI negasit: " + ex.getClass().getSimpleName()); log("ai err " + ex); }
        });
    }
    private static String esc(String s) { return s == null ? "" : s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", ""); }

    // optionally mirror ! into /ai if read_chat is on
    @EventHandler(ignoreCancelled = false)
    public void onChat(AsyncPlayerChatEvent e) {
        if (!getConfig().getBoolean("read_chat", false)) return;
        String m = e.getMessage();
        if (m.length() > 2 && m.charAt(0) == '!' && m.charAt(1) == 'a' && m.charAt(2) == 'i' && (m.length() == 3 || m.charAt(3) == ' ')) {
            e.setCancelled(true);
            String[] a = m.substring(3).trim().isEmpty() ? new String[0] : m.substring(4).trim().split("\\s+");
            Bukkit.getScheduler().runTask(this, () -> onAi(e.getPlayer(), null, "ai", a));
        }
    }
}
