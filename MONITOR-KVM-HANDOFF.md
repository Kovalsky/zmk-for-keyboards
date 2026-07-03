# Monitor KVM switching — передача для наступної сесії

> ✅ **ВИКОНАНО 2026-07-04.** Систему зібрано: `mon-to-mac` / `mon-to-laptop` /
> `mon-ddc-set` у `~/.local/bin`, evdev-листенер + `mon-kvm-hotkey.service`, макроси
> `kvm_to_mac` / `kvm_to_laptop` у keymap (ADJUST → `→MAC` / `→UBU`), правило Karabiner
> на Mac'у. Деталі — розділ «Зроблено (2026-07-04)» у `MONITOR-KVM.md`. Лишилось user'у:
> `sudo apt install openssh-server`, Mac Wi-Fi → Fixed + Apple TV увімкн., перепрошити Lily.

**Мета:** одна клавіша на Lily58 перемикає монітор Samsung + мишу (через KVM монітора) +
клавіатуру (BT-профіль) між Ubuntu-ноутом і MacBook. Як фізична кнопка монітора, але з клавіатури.

**Технічна довідка з усіма деталями DDC/входів/пробудження:** див. `MONITOR-KVM.md` у цьому ж репо.
Цей файл — лише стан + що робити далі. Дата сесії: 2026-07-03.

---

## ✅ Зроблено і ПЕРЕВІРЕНО наживо (не переробляти)

1. **Перемикання відео+миші обома напрямками — працює миттєво.** Обидві машини на керованих
   входах монітора. Команди виконує Ubuntu (його HDMI-DDC живий завжди):
   - На Mac: `ddcutil --bus 4 setvcp 60 0x0f`
   - На Ubuntu: `ddcutil --bus 4 setvcp 60 0x05`
   - Перевірка: миша (Razer) при 0x0f зникла з `lsusb` Ubuntu і з'явилась у `ioreg` Mac; при 0x05 повернулась.
2. **Конфіг монітора виставлено:** System → USB Source Setup: `HDMI→USB-B`, `DisplayPort→USB-C`;
   Auto Source Switch+ = Off.
3. **Кабелі Mac:** USB-C→DisplayPort (відео в DP-порт) + звичайний USB-C (дані KVM + 90 Вт заряд).
4. **Пробудження сплячого Mac по Wi-Fi — працює** (2 кроки, перевірено `pmset -g log`):
   магічний пакет (WoL) підіймає лише мережу (DarkWake), а `caffeinate -u` по SSH одразу після —
   доводить до повного Wake з увімкненим екраном. Потрібен увімкнений Apple TV (sleep-proxy) у мережі.

## ❌ Що НЕ вийшло (не витрачати час знову)

- Перемкнутись **на USB-C-вхід** командою — заблоковано прошивкою (перебрано всі 255 кодів). Саме тому Mac переехав на DisplayPort.
- **Вимкнений** (Shut Down) Mac розбудити по мережі — неможливо (WoL тільки зі сну). Порада user'у: «вимикати» = Sleep.
- Керувати монітором з боку Mac (ddcctl/BetterDisplay DDC мертві на macOS 15) — тому всі DDC-команди робить Ubuntu.
- Трюк «погасити HDMI, хай монітор сам знайде Mac» — монітор просто засинає.

## 🎯 Обраний дизайн (user підтвердив): ОДИН Lily-акорд, обидва боки

- **Ubuntu → Mac:** Lily шле хоткей (поки на Ubuntu-профілі) → Ubuntu ловить evdev-листенером →
  запускає `mon-to-mac` → потім Lily перемикає BT-профіль на Mac.
- **Mac → Ubuntu:** Lily шле хоткей (поки на Mac-профілі) → Mac ловить Karabiner'ом →
  `ssh ubuntu 'mon-to-laptop'` → потім Lily перемикає BT-профіль на Ubuntu.
  (Команду мусить виконати Ubuntu, бо Mac по DDC не вміє.)

---

## 📋 ЗРОБИТИ в наступній сесії (по порядку)

1. **Скрипти на Ubuntu** (`~/.local/bin/`) — я НЕ встиг створити:
   - `mon-to-laptop`: `ddcutil --bus 4 setvcp 60 0x05` у циклі-повторі (Samsung input-switch буває
     з 2-3 спроби, ddcutil #398), поки `getvcp 60` не поверне `x05`.
   - `mon-to-mac`: (а) WoL магічний пакет на Wi-Fi-MAC Mac'а (слати на broadcast :9); (б) цикл
     `ssh falco@<mac> 'nohup caffeinate -u -t 30 &'` поки не з'єднається (підняти+утримати повний
     wake; no-op якщо Mac не спав); (в) `setvcp 60 0x0f` у циклі-повторі до `x0f`. ~5-8с зі сну.
   - Дзеркалити стиль/права як у `~/tools/whisper-dictate/` (i2c-група вже додана user'у —
     активна після перелогіну; інакше `sg i2c -c '...'`).
2. **evdev-хоткей на Ubuntu** — мірор `~/tools/whisper-dictate/hotkey-listener.py` + systemd-user
   unit. Ловить хоткей від Lily → `mon-to-mac`. **Вільні F-клавіші:** F6/F7/F9 зайняті диктовкою,
   F10/F11/F12 — meeting. Взяти вільну (напр. F13+) або комбо.
3. **SSH-сервер на Ubuntu** — зараз `inactive`. User вмикає: `sudo systemctl enable --now ssh`.
   Потім авторизувати ключ Mac→Ubuntu (Mac's pubkey у `~/.ssh/authorized_keys` на Ubuntu) — для
   зворотного напрямку.
4. **Karabiner на Mac** — хоткей → `ssh <ubuntu> 'mon-to-laptop'`.
5. **ZMK keymap Lily** (`config/lily58.keymap`, `&bt BT_SEL 0..4` у рядку ~204): два акорди,
   кожен = tap хоткею + `&macro_wait_time` + `&bt BT_SEL <n>`. Перепрошити обидві половини
   (workflow у пам'яті: feedback_download_builds).

## ❓ Спитати в user'а на старті

- Які саме хоткеї/комбо повісити (щоб не конфліктували з наявними evdev-листенерами).
- Який номер BT-профілю Lily = Ubuntu, який = Mac (`BT_SEL <n>`).
- **Зафіксувати приватну Wi-Fi-адресу Macّа** (System Settings → Wi-Fi → мережа → Private Wi-Fi
  Address → **Fixed**), бо «rotating» зламає WoL, коли MAC зміниться.

## 🔑 Ключові значення

- Монітор DDC: шина `--bus 4`. Коди VCP 60: `0x05`=HDMI(Ubuntu), `0x0f`=DP(Mac), `0x01`=USB-C(заблок., не використ.), `0x06`=фантом.
- Mac: `falco@192.168.0.103` (MacBook-Pro-Bohdan.local), MacBookPro15,1 Intel, macOS 15.7. SSH Ubuntu→Mac вже налаштований.
- Wi-Fi-MAC Mac (для WoL): приватний `4e:b2:55:a3:78:18` (на повітрі), апаратний `a4:83:e7:1f:e9:ac`. Слати на обидва.
- Apple TV sleep-proxy: «Living Room» `192.168.0.113` — має бути УВІМКНЕНИЙ для Wi-Fi-пробудження.
- WoL-сендер (python, без залежностей) — був у scratchpad; логіка: `ff`×6 + MAC×16 на UDP broadcast :9.

## ⚠️ Пастки цієї сесії (не повторити)

- Миша зникла з `lsusb` ≠ KVM перемкнувся: сон USB-хаба виглядає так само. Перевіряти обома боками.
- Пінг відповідає ≠ Mac повністю прокинувся: DarkWake теж піднімає мережу. Перевіряти
  `ioreg -n IODisplayWrangler … CurrentPowerState` (4=екран увімк) або `pmset -g log`.
- Оболонка тут **zsh**: `VAR="ssh …"; $VAR cmd` НЕ розбивається на слова — виклик падає. Кликати `ssh` напряму.
- Видимі тести на моніторі — ≤6 секунд без окремого дозволу user'а (довше — питати).
- Не під'єднувати Ethernet до монітора (user: тільки Wi-Fi). Не писати наосліп у вендорні VCP Samsung (ризик закирпичити).
