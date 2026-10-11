# ENGINE HOST AB — gazda reala, copii izolate pe :25566

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38122349973
NU este test cu un client real; serverul public :25565 a ramas neatins.

```json
{
  "method": "two PRIVATE copies on the actual live host; live JVM stays up; no real players",
  "disclaimer": "Synthetic workload only. Does NOT establish client handshake or universal superiority.",
  "world_copied": "world",
  "live_jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
  "baseline-2023": {
    "label": "baseline-2023",
    "boot_done_s": null,
    "plugins_enabled": 0,
    "mods_on_disk": 36,
    "rss_median_mb": null,
    "rss_peak_mb": null,
    "spark_tick_min_median_p95_max_ms_1m": null,
    "critical_errors": [],
    "exit_code": 143,
    "clean_stop": false,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "command_feedback_last": [],
    "valid": false,
    "log_tail_on_failure": [
      "[07:48:07] [modloading-worker-0/INFO]: RoadStuff setup started!",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:aluminum_boat from classpath:/assets/vehicle/vehicles/aluminum_boat.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:couch from classpath:/assets/vehicle/vehicles/couch.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:sofacopter from classpath:/assets/vehicle/vehicles/sofacopter.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:police_investigation_car from classpath:/assets/vehicle/vehicles/police_investigation_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:schneemobil from classpath:/assets/vehicle/vehicles/schneemobil.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:dirt_bike from classpath:/assets/vehicle/vehicles/dirt_bike.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:lawn_mower from classpath:/assets/vehicle/vehicles/lawn_mower.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:atv_mark2 from classpath:/assets/vehicle/vehicles/atv_mark2.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:go_kart from classpath:/assets/vehicle/vehicles/go_kart.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:off_roader from classpath:/assets/vehicle/vehicles/off_roader.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:tractor from classpath:/assets/vehicle/vehicles/tractor.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:fluid_trailer from classpath:/assets/vehicle/vehicles/fluid_trailer.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:post_car from classpath:/assets/vehicle/vehicles/post_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:bumper_car from classpath:/assets/vehicle/vehicles/bumper_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:luxuswagen from classpath:/assets/vehicle/vehicles/luxuswagen.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:bimmelbahn_passagierwagon from classpath:/assets/vehicle/vehicles/bimmelbahn_passagierwagon.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:sports_plane from classpath:/assets/vehicle/vehicles/sports_plane.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:basilico_gt from classpath:/assets/vehicle/vehicles/basilico_gt.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:storage_trailer from classpath:/assets/vehicle/vehicles/storage_trailer.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:fib_transport_car from classpath:/assets/vehicle/vehicles/fib_transport_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:couch_rainbow from classpath:/assets/vehicle/vehicles/couch_rainbow.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:speed_boat from classpath:/assets/vehicle/vehicles/speed_boat.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:taxi_car from classpath:/assets/vehicle/vehicles/taxi_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:police_transport_car from classpath:/assets/vehicle/vehicles/police_transport_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:pizza_tokens_car from classpath:/assets/vehicle/vehicles/pizza_tokens_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:pizza_brew_car from classpath:/assets/vehicle/vehicles/pizza_brew_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:vehicle_trailer from classpath:/assets/vehicle/vehicles/vehicle_trailer.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:fib_car from classpath:/assets/vehicle/vehicles/fib_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:go_kart_mark2 from classpath:/assets/vehicle/vehicles/go_kart_mark2.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:pizza_sportwagen_car from classpath:/assets/vehicle/vehicles/pizza_sportwagen_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:ambulance_car from classpath:/assets/vehicle/vehicles/ambulance_car.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:fertilizer from classpath:/assets/vehicle/vehicles/fertilizer.json",
      "[07:48:07] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:jet_ski from classpath:/assets/vehicle/vehicles/jet_ski.json",
      "[07:48:08] [modloading-worker-0/INFO]: 12 Karten erfolgreich geladen."
    ]
  },
  "status": "ABORTED / NO LIVE JAR CHANGED",
  "reason": "baseline-2023 failed isolated boot/spark; no other test run"
}
```
