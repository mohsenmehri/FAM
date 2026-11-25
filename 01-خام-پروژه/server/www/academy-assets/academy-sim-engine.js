/* FAM Academy Interactive Protocol & Educational IOS CLI Simulator Engine.
 * Pure educational logic: no DOM, no network calls, no real device access.
 * Exposed as window.FAMAcademySimEngine in browsers and CommonJS in Node tests.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.FAMAcademySimEngine = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var OUTPUT_LABEL = 'Sample / Simulated — Internal Simulator';

  function ipToInt(ip) {
    var parts = String(ip || '').trim().split('.');
    if (parts.length !== 4) throw new Error('آدرس IPv4 باید دقیقاً چهار اکتت داشته باشد.');
    var n = 0;
    for (var i = 0; i < 4; i += 1) {
      if (!/^\d+$/.test(parts[i])) throw new Error('اکتت IPv4 نامعتبر است.');
      var v = Number(parts[i]);
      if (!Number.isInteger(v) || v < 0 || v > 255) throw new Error('مقدار اکتت باید بین 0 تا 255 باشد.');
      n = ((n << 8) + v) >>> 0;
    }
    return n >>> 0;
  }

  function maskInt(prefix) {
    var p = Number(prefix);
    if (!Number.isInteger(p) || p < 0 || p > 32) throw new Error('پیشوند (Prefix) باید بین 0 تا 32 باشد.');
    if (p === 0) return 0;
    return (0xffffffff << (32 - p)) >>> 0;
  }

  function sameSubnet(a, b, prefix) {
    var m = maskInt(prefix);
    return ((ipToInt(a) & m) >>> 0) === ((ipToInt(b) & m) >>> 0);
  }

  function macFor(ip) {
    var last = ipToInt(ip) & 255;
    return '02:00:00:00:00:' + last.toString(16).padStart(2, '0').toUpperCase();
  }

  function bool(v) {
    return v === true || v === 'true' || v === 'on' || v === 1 || v === '1';
  }

  function num(v, fallback) {
    var n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  }

  function parseAllowed(text) {
    var seen = new Set();
    var out = [];
    String(text || '')
      .split(/[,\s]+/)
      .forEach(function (part) {
        var trimmed = part.trim();
        if (!trimmed) return;
        if (/^\d+-\d+$/.test(trimmed)) {
          var bounds = trimmed.split('-').map(Number);
          var lo = Math.max(1, Math.min(bounds[0], bounds[1]));
          var hi = Math.min(4094, Math.max(bounds[0], bounds[1]));
          for (var v = lo; v <= hi && out.length < 256; v += 1) {
            if (!seen.has(v)) { seen.add(v); out.push(v); }
          }
          return;
        }
        var n = Number(trimmed);
        if (Number.isInteger(n) && n >= 1 && n <= 4094 && !seen.has(n)) {
          seen.add(n);
          out.push(n);
        }
      });
    return out;
  }

  function arpResolve(params) {
    params = params || {};
    try {
      var sourceIp = String(params.sourceIp || '192.0.2.10').trim();
      var targetIp = String(params.targetIp || '192.0.2.20').trim();
      var gatewayIp = String(params.gatewayIp || '192.0.2.1').trim();
      var prefix = num(params.mask, 24);
      var cacheHit = bool(params.cacheHit);
      var vlanId = num(params.vlanId, 10);
      ipToInt(sourceIp);
      ipToInt(targetIp);
      ipToInt(gatewayIp);
      maskInt(prefix);

      var local = sameSubnet(sourceIp, targetIp, prefix);
      var gwLocal = sameSubnet(sourceIp, gatewayIp, prefix);
      var warnings = [];
      if (!local && !gwLocal) {
        warnings.push('آدرس Default Gateway خارج از ساب‌نت مبدأ قرار دارد؛ در شبکه واقعی میزبان به این Gateway دسترسی نخواهد داشت.');
      }
      if (cacheHit) {
        warnings.push('گزینه Cache Hit فعال است؛ برای مشاهده بسته Broadcast درخواست ARP، آن را خاموش کنید.');
      } else {
        warnings.push('Proxy ARP و Gratuitous ARP در این مدل آموزشی شبیه‌سازی نشده‌اند.');
      }

      var arpTargetIp = local ? targetIp : gatewayIp;
      var srcMac = macFor(sourceIp);
      var targetMac = macFor(arpTargetIp);
      var steps = [];
      var table = [];
      var t = 0;

      function add(title, from, to, protocol, message, detail, size) {
        var row = {
          index: steps.length + 1,
          time: (t / 1000).toFixed(3) + 's',
          from: from,
          to: to,
          protocol: protocol,
          message: message,
          detail: detail,
          size: size,
          title: title
        };
        steps.push(row);
        table.push(row);
        t += 12;
      }

      add(
        'بررسی ساب‌نت مبدأ و مقصد',
        sourceIp,
        '—',
        'IPv4',
        'Compare ' + sourceIp + '/' + prefix + ' with ' + targetIp,
        local
          ? 'مقصد در همان ساب‌نت محلی است؛ میزبان مستقیماً ARP را برای IP مقصد اجرا می‌کند.'
          : 'مقصد در ساب‌نت دیگری است؛ میزبان باید آدرس MAC مربوط به Default Gateway را بیابد.',
        '0 B'
      );
      add(
        'انتخاب هدف ARP',
        sourceIp,
        arpTargetIp,
        'ARP',
        'Resolve L2 address for ' + arpTargetIp,
        local
          ? 'Next-Hop L2 = ' + targetIp
          : 'Next-Hop L2 = ' + gatewayIp + ' (در حالی که IP مقصد نهایی همچنان ' + targetIp + ' باقی می‌ماند).',
        '28 B'
      );
      if (cacheHit) {
        add(
          'یافتن در ARP Cache',
          sourceIp,
          arpTargetIp,
          'ARP',
          'Cache hit: ' + arpTargetIp + ' -> ' + targetMac,
          'نگاشت از قبل در حافظه ARP میزبان موجود است؛ هیچ Broadcast ارسال نمی‌شود.',
          '0 B'
        );
      } else {
        add(
          'ارسال ARP Request',
          sourceIp,
          'ff:ff:ff:ff:ff:ff',
          'ARP',
          'Who has ' + arpTargetIp + '? Tell ' + sourceIp,
          'فریم Broadcast در VLAN ' + vlanId + ' توسط سوئیچ به همه پورت‌های همان VLAN ارسال (Flood) می‌شود.',
          '42 B'
        );
        add(
          'دریافت ARP Reply',
          arpTargetIp,
          sourceIp,
          'ARP',
          arpTargetIp + ' is at ' + targetMac,
          'میزبان هدف یا روتر پاسخ Unicast برمی‌گرداند و جدول ARP فرستنده به‌روز می‌شود.',
          '42 B'
        );
      }
      add(
        'ساخت فریم نهایی لایه ۲ و ۳',
        sourceIp,
        targetIp,
        'IPv4 / Ethernet',
        local ? 'Frame -> ' + targetMac + ' (IP dst ' + targetIp + ')' : 'Frame -> Gateway ' + targetMac + ' (IP dst ' + targetIp + ')',
        'Src MAC = ' + srcMac + ' | Dst MAC = ' + targetMac + ' | Src IP = ' + sourceIp + ' | Dst IP = ' + targetIp,
        '98 B'
      );

      return {
        ok: true,
        logic: 'arpResolve',
        label: OUTPUT_LABEL,
        decision: local ? 'تحویل محلی (Local Delivery)' : 'تحویل از طریق Gateway',
        summary: local
          ? 'مقصد در همان ساب‌نت /' + prefix + ' است؛ ARP مستقیماً MAC آدرس ' + targetIp + ' (' + targetMac + ') را کشف کرد.'
          : 'مقصد خارج از ساب‌نت است؛ ARP برای Default Gateway (' + gatewayIp + ') انجام شد، ولی بسته IP همچنان به مقصد ' + targetIp + ' آدرس‌دهی شده است.',
        params: { sourceIp: sourceIp, targetIp: targetIp, gatewayIp: gatewayIp, mask: prefix, cacheHit: cacheHit, vlanId: vlanId },
        steps: steps,
        table: table,
        warnings: warnings,
        limitations: [
          'این مدل فقط آدرس‌های IPv4 با Prefix بین 0 تا 32 را بررسی می‌کند.',
          'آدرس‌های MAC و زمان‌ها مقادیر آموزشی (Designed/Simulated) هستند و از سخت‌افزار واقعی خوانده نشده‌اند.'
        ]
      };
    } catch (e) {
      return {
        ok: false,
        logic: 'arpResolve',
        label: OUTPUT_LABEL,
        error: String(e && e.message ? e.message : e),
        steps: [],
        table: [],
        warnings: ['ورودی IPv4 یا Prefix نامعتبر است.']
      };
    }
  }

  function vlanForward(params) {
    params = params || {};
    var sourceVlan = num(params.sourceVlan, 10);
    var destinationVlan = num(params.destinationVlan, sourceVlan);
    var nativeVlan = num(params.nativeVlan, 99);
    var remoteNativeVlan = num(params.remoteNativeVlan, nativeVlan);
    var allowed = parseAllowed(params.trunkAllowed || '10,20,99');
    var tagNative = bool(params.tagNative);
    var allowedSet = new Set(allowed);
    var warnings = [];
    var steps = [];
    var table = [];
    var dropReason = null;

    function add(title, from, to, protocol, message, detail, size) {
      var row = {
        index: steps.length + 1,
        time: (steps.length * 0.012).toFixed(3) + 's',
        from: from,
        to: to,
        protocol: protocol,
        message: message,
        detail: detail,
        size: size,
        title: title
      };
      steps.push(row);
      table.push(row);
    }

    add(
      'دریافت فریم روی پورت Access',
      'Host A',
      'SW1',
      'Ethernet',
      'Untagged frame -> VLAN ' + sourceVlan,
      'سوئیچ SW1 فریم بدون برچسب را از پورت Access می‌گیرد و به VLAN ' + sourceVlan + ' منسوب می‌کند.',
      '64 B'
    );

    var allowedOk = allowedSet.has(sourceVlan);
    add(
      'بررسی Allowed VLAN List',
      'SW1',
      'Trunk Link',
      '802.1Q',
      allowedOk ? 'VLAN ' + sourceVlan + ' allowed' : 'VLAN ' + sourceVlan + ' BLOCKED',
      allowedOk
        ? 'لیست مجاز Trunk شامل: ' + (allowed.join(', ') || 'هیچ')
        : 'VLAN ' + sourceVlan + ' در Allowed VLAN List لینک Trunk نیست؛ فریم حذف می‌شود.',
      allowedOk ? '0 B' : 'DROPPED'
    );
    if (!allowedOk) dropReason = 'VLAN ' + sourceVlan + ' در لیست Allowed VLANهای Trunk مجاز نیست.';

    var isNative = sourceVlan === nativeVlan;
    var tagged = !isNative || tagNative;
    add(
      'تصمیم برچسب‌گذاری 802.1Q',
      'SW1',
      'SW2',
      '802.1Q',
      tagged ? 'Tagged VID=' + sourceVlan : 'Untagged (Native VLAN ' + nativeVlan + ')',
      tagged
        ? 'هدر ۴ بایتی 802.1Q با شناسه VID=' + sourceVlan + ' به فریم اضافه می‌شود.'
        : 'به صورت پیش‌فرض فریم‌های Native VLAN بدون Tag از Trunk عبور می‌کنند.',
      tagged ? '68 B' : '64 B'
    );

    if (isNative && !tagNative && remoteNativeVlan !== nativeVlan) {
      warnings.push('Native VLAN Mismatch: SW1 فریم Untagged را از VLAN ' + nativeVlan + ' می‌فرستد، ولی SW2 آن را در VLAN ' + remoteNativeVlan + ' دریافت می‌کند (خطر VLAN Hopping / اختلال ترافیک).');
      dropReason = 'ناهمگونی Native VLAN میان دو سر لینک Trunk (' + nativeVlan + ' در برابر ' + remoteNativeVlan + ').';
    }
    if (isNative && tagNative) {
      warnings.push('Tag کردن Native VLAN فعال است (vlan dot1q tag native)؛ ابهام فریم Untagged از بین رفت.');
    }

    var l2Delivery = allowedOk && !dropReason && sourceVlan === destinationVlan;
    add(
      'عبور از لینک Trunk',
      'SW1',
      'SW2',
      '802.1Q',
      allowedOk && !dropReason ? 'Frame crosses trunk' : 'Frame discarded / mismatched',
      allowedOk && !dropReason
        ? 'لینک Trunk ترافیک چند VLAN را با حفظ مرز هر Broadcast Domain منتقل می‌کند.'
        : dropReason,
      allowedOk && !dropReason ? (tagged ? '68 B' : '64 B') : 'DROPPED'
    );
    add(
      'تحویل لایه ۲ در مقصد',
      'SW2',
      'Host B',
      'Ethernet',
      l2Delivery ? 'Delivered untagged in VLAN ' + destinationVlan : 'No L2 delivery',
      l2Delivery
        ? 'برچسب 802.1Q برداشته شده و فریم عادی تحویل Host B در VLAN ' + destinationVlan + ' می‌شود.'
        : (sourceVlan !== destinationVlan
          ? 'مقصد در VLAN ' + destinationVlan + ' قرار دارد؛ ارتباط بین دو VLAN بدون روتر یا SVI (لایه ۳) امکان‌پذیر نیست.'
          : dropReason),
      l2Delivery ? '64 B' : 'DROPPED'
    );
    if (sourceVlan !== destinationVlan) {
      warnings.push('برای ارتباط میان VLAN ' + sourceVlan + ' و VLAN ' + destinationVlan + ' به مسیریابی لایه ۳ (Router-on-a-Stick یا SVI) نیاز است.');
    }

    return {
      ok: true,
      logic: 'vlanForward',
      label: OUTPUT_LABEL,
      decision: l2Delivery ? 'تحویل موفق لایه ۲' : 'حذف / نیازمند مسیریابی لایه ۳',
      summary: l2Delivery
        ? 'فریم VLAN ' + sourceVlan + (tagged ? ' به‌صورت Tagged' : ' به‌صورت Untagged/Native') + ' از Trunk عبور کرد و در همان VLAN تحویل شد.'
        : 'تحویل لایه ۲ انجام نشد: ' + (dropReason || 'مبدأ و مقصد در دو VLAN متفاوت قرار دارند.'),
      params: {
        sourceVlan: sourceVlan,
        destinationVlan: destinationVlan,
        nativeVlan: nativeVlan,
        remoteNativeVlan: remoteNativeVlan,
        allowed: allowed,
        tagNative: tagNative
      },
      steps: steps,
      table: table,
      warnings: warnings,
      limitations: [
        'پروتکل‌های STP، DTP، VTP و QoS در این شبیه‌ساز ساده مدل نشده‌اند.',
        'سناریو فقط یک لینک Trunk بین دو سوئیچ را بررسی می‌کند.'
      ]
    };
  }

  function ospfAdjacency(params) {
    params = params || {};
    var area = String(params.areaId != null ? params.areaId : '0').trim();
    var remoteArea = String(params.remoteAreaId != null ? params.remoteAreaId : area).trim();
    var hello = num(params.hello, 10);
    var remoteHello = num(params.remoteHello, hello);
    var dead = num(params.dead, 40);
    var remoteDead = num(params.remoteDead, dead);
    var auth = String(params.auth || 'none');
    var remoteAuth = String(params.remoteAuth || auth);
    var mtu = num(params.mtu, 1500);
    var remoteMtu = num(params.remoteMtu, mtu);
    var networkType = String(params.networkType || 'broadcast');
    var priority = num(params.priority, 1);

    var mismatches = [];
    if (area !== remoteArea) mismatches.push('Area ID (' + area + ' در برابر ' + remoteArea + ')');
    if (hello !== remoteHello) mismatches.push('Hello Interval (' + hello + 's در برابر ' + remoteHello + 's)');
    if (dead !== remoteDead) mismatches.push('Dead Interval (' + dead + 's در برابر ' + remoteDead + 's)');
    if (auth !== remoteAuth) mismatches.push('Authentication (' + auth + ' در برابر ' + remoteAuth + ')');
    var mtuMismatch = mtu !== remoteMtu;
    if (mtuMismatch) mismatches.push('Interface MTU (' + mtu + ' در برابر ' + remoteMtu + ')');

    var sequence = ['Down', 'Init', '2-Way', 'ExStart', 'Exchange', 'Loading', 'Full'];
    var stopIndex = sequence.length - 1;
    var finalState = 'Full';
    var reason = 'تمام پارامترهای Hello و MTU سازگار هستند و LSDB کامل همگام‌سازی شد.';

    if (mismatches.length) {
      if (area !== remoteArea || hello !== remoteHello || dead !== remoteDead || auth !== remoteAuth) {
        stopIndex = 1;
      } else {
        stopIndex = 3;
      }
      finalState = sequence[stopIndex];
      reason = 'عدم تطابق پارامترها: ' + mismatches.join('، ') + '.';
    } else if (networkType === 'broadcast' && priority === 0) {
      stopIndex = 2;
      finalState = '2-Way';
      reason = 'روتر با Priority=0 در نقش DROther باقی می‌ماند؛ بین دو DROther همسایگی در حالت 2-Way می‌ماند (Adjacency کامل فقط با DR/BDR تشکیل می‌شود).';
    }

    var detailByState = {
      Down: 'هنوز بسته Hello معتبری از همسایه دریافت نشده است.',
      Init: 'بسته Hello دریافت شد ولی Router ID محلی هنوز در فهرست همسایه‌های طرف مقابل نیست.',
      '2-Way': 'ارتباط دوسویه برقرار است؛ در شبکه Broadcast/NBMA انتخاب DR و BDR انجام می‌شود.',
      ExStart: 'تعیین نقش Master/Slave و شماره توالی اولیه DBD؛ در صورت اختلاف MTU همسایگی اینجا متوقف می‌شود.',
      Exchange: 'مبادله خلاصه LSDB از طریق بسته‌های Database Description (DBD).',
      Loading: 'ارسال LSR برای دریافت LSAهای جدیدتر و تایید با LSU و LSAck.',
      Full: 'پایگاه داده لینک‌استیت (LSDB) کاملاً یکسان است و الگوریتم SPF اجرا می‌شود.'
    };

    var steps = [];
    var table = [];
    for (var i = 0; i <= stopIndex; i += 1) {
      var st = sequence[i];
      var row = {
        index: i + 1,
        time: (i * 0.015).toFixed(3) + 's',
        from: 'R1',
        to: 'R2',
        protocol: 'OSPFv2',
        message: st,
        detail: detailByState[st],
        size: st === 'Down' ? '0 B' : 'Hello / DBD',
        title: st
      };
      steps.push(row);
      table.push(row);
    }
    if (stopIndex < sequence.length - 1) {
      var stopRow = {
        index: steps.length + 1,
        time: ((stopIndex + 1) * 0.015).toFixed(3) + 's',
        from: 'R1',
        to: 'R2',
        protocol: 'OSPFv2',
        message: 'STOPPED at ' + finalState,
        detail: reason,
        size: '—',
        title: 'توقف در ' + finalState
      };
      steps.push(stopRow);
      table.push(stopRow);
    }

    return {
      ok: true,
      logic: 'ospfAdjacency',
      label: OUTPUT_LABEL,
      decision: finalState,
      summary: finalState === 'Full'
        ? 'همسایگی OSPF با موفقیت به حالت Full رسید؛ Area، تایمرها، احراز هویت و MTU یکسان بودند.'
        : 'ماشین حالت در ' + finalState + ' متوقف شد: ' + reason,
      params: {
        areaId: area,
        remoteAreaId: remoteArea,
        hello: hello,
        remoteHello: remoteHello,
        dead: dead,
        remoteDead: remoteDead,
        auth: auth,
        remoteAuth: remoteAuth,
        mtu: mtu,
        remoteMtu: remoteMtu,
        networkType: networkType,
        priority: priority
      },
      finalState: finalState,
      steps: steps,
      table: table,
      warnings: mismatches.length ? mismatches : (priority === 0 ? ['Priority=0 مانع انتخاب روتر به‌عنوان DR/BDR می‌شود.'] : []),
      limitations: [
        'مدل آموزشی OSPFv2 است؛ انواع پیچیده LSA (Type 3/4/5) و OSPFv3 پیاده‌سازی نشده‌اند.',
        'بررسی Passive Interface و Subnet Mask در یک لینک مستقیم فرض شده است.'
      ]
    };
  }

  function normalizeInterface(name) {
    var n = String(name || '').trim();
    var m;
    if ((m = n.match(/^(?:gi|gigabitethernet)\s*(\d+(?:\/\d+)*)$/i))) return 'GigabitEthernet' + m[1];
    if ((m = n.match(/^(?:fa|fastethernet)\s*(\d+(?:\/\d+)*)$/i))) return 'FastEthernet' + m[1];
    if ((m = n.match(/^(?:lo|loopback)\s*(\d+)$/i))) return 'Loopback' + m[1];
    if ((m = n.match(/^(?:vl|vlan)\s*(\d+)$/i))) return 'Vlan' + m[1];
    return n;
  }

  function createLabState(lab) {
    return {
      labId: lab && lab.id ? lab.id : 'lab',
      mode: 'user',
      hostname: lab && lab.defaultHostname ? lab.defaultHostname : 'Switch',
      currentInterface: null,
      currentVlan: null,
      interfaces: {},
      vlans: { 1: { id: 1, name: 'default', ports: [] } },
      ospfNetworks: [],
      ospfProcess: null,
      passiveInterfaces: [],
      executed: [],
      label: OUTPUT_LABEL,
      realDeviceConnection: false
    };
  }

  function removePortFromAllVlans(state, iface) {
    Object.keys(state.vlans).forEach(function (k) {
      var v = state.vlans[k];
      v.ports = v.ports.filter(function (p) { return p !== iface; });
    });
  }

  function runLabCommand(state, raw) {
    var cmd = String(raw || '').trim().replace(/\s+/g, ' ');
    var out = [];
    var matched = true;
    function push(line) { out.push(String(line)); }
    if (!cmd) return { state: state, output: [], matched: true, label: OUTPUT_LABEL, command: '' };
    state.executed.push(cmd);

    var isPrivOrAbove = state.mode !== 'user';
    var isConfigOrSub = state.mode === 'config' || state.mode === 'interface' || state.mode === 'vlan' || state.mode === 'router';

    if (/^enable$/i.test(cmd)) {
      state.mode = 'privileged';
      push('% Simulator: entered privileged EXEC mode (' + state.hostname + '#).');
    } else if (/^disable$/i.test(cmd)) {
      state.mode = 'user';
      state.currentInterface = null;
      state.currentVlan = null;
      push('% Simulator: returned to user EXEC mode (' + state.hostname + '>).');
    } else if (/^(?:configure terminal|conf t)$/i.test(cmd)) {
      if (!isPrivOrAbove) {
        matched = false;
        push('% Privileged mode required. Run "enable" first.');
      } else {
        state.mode = 'config';
        state.currentInterface = null;
        state.currentVlan = null;
        push('Enter configuration commands, one per line. End with CNTL/Z.');
      }
    } else if (/^end$/i.test(cmd)) {
      if (!isConfigOrSub) {
        matched = false;
        push('% Not in configuration mode.');
      } else {
        state.mode = 'privileged';
        state.currentInterface = null;
        state.currentVlan = null;
        push('% Simulator: returned to privileged EXEC mode.');
      }
    } else if (/^exit$/i.test(cmd)) {
      if (state.mode === 'interface' || state.mode === 'vlan' || state.mode === 'router') {
        state.mode = 'config';
        state.currentInterface = null;
        state.currentVlan = null;
      } else if (state.mode === 'config') {
        state.mode = 'privileged';
      } else if (state.mode === 'privileged') {
        state.mode = 'user';
      }
      push('% Simulator: mode is now ' + state.mode + '.');
    } else if (/^hostname\s+\S+$/i.test(cmd)) {
      if (!isConfigOrSub) {
        matched = false;
        push('% Invalid input detected. Enter global config mode ("configure terminal") first.');
      } else {
        state.hostname = cmd.split(/\s+/)[1];
        push('% Simulator: hostname set to ' + state.hostname + '.');
      }
    } else if (/^vlan\s+(\d+)$/i.test(cmd)) {
      if (!isConfigOrSub) {
        matched = false;
        push('% Invalid input detected. Enter global config mode ("configure terminal") first.');
      } else {
        var vid = Number(cmd.match(/^vlan\s+(\d+)$/i)[1]);
        if (vid < 1 || vid > 4094) {
          matched = false;
          push('% Invalid VLAN ID (must be 1..4094).');
        } else {
          state.vlans[vid] = state.vlans[vid] || { id: vid, name: 'VLAN' + String(vid).padStart(4, '0'), ports: [] };
          state.currentVlan = vid;
          state.currentInterface = null;
          state.mode = 'vlan';
          push('% Simulator: VLAN ' + vid + ' selected.');
        }
      }
    } else if (/^name\s+\S+/i.test(cmd)) {
      if (state.mode !== 'vlan' || !state.currentVlan) {
        matched = false;
        push('% Invalid input detected. Select a VLAN first (e.g. "vlan 10").');
      } else {
        state.vlans[state.currentVlan].name = cmd.replace(/^name\s+/i, '').trim();
        push('% Simulator: VLAN ' + state.currentVlan + ' renamed to ' + state.vlans[state.currentVlan].name + '.');
      }
    } else if (/^(?:interface|int)\s+.+$/i.test(cmd)) {
      if (!isConfigOrSub) {
        matched = false;
        push('% Invalid input detected. Enter global config mode ("configure terminal") first.');
      } else {
        var iface = normalizeInterface(cmd.replace(/^(?:interface|int)\s+/i, ''));
        state.currentInterface = iface;
        state.currentVlan = null;
        state.interfaces[iface] = state.interfaces[iface] || {
          name: iface,
          mode: '',
          vlan: null,
          ip: null,
          ipv6: null,
          shutdown: false,
          trunkAllowed: [],
          nativeVlan: null
        };
        state.mode = 'interface';
        push('% Simulator: interface ' + iface + ' selected.');
      }
    } else if (/^switchport mode access$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        state.interfaces[state.currentInterface].mode = 'access';
        push('% Simulator: ' + state.currentInterface + ' set to access mode.');
      }
    } else if (/^switchport access vlan\s+(\d+)$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        var av = Number(cmd.match(/vlan\s+(\d+)/i)[1]);
        removePortFromAllVlans(state, state.currentInterface);
        state.interfaces[state.currentInterface].vlan = av;
        state.vlans[av] = state.vlans[av] || { id: av, name: 'VLAN' + String(av).padStart(4, '0'), ports: [] };
        if (state.vlans[av].ports.indexOf(state.currentInterface) === -1) {
          state.vlans[av].ports.push(state.currentInterface);
        }
        push('% Simulator: ' + state.currentInterface + ' assigned to VLAN ' + av + '.');
      }
    } else if (/^switchport mode trunk$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        removePortFromAllVlans(state, state.currentInterface);
        state.interfaces[state.currentInterface].mode = 'trunk';
        state.interfaces[state.currentInterface].vlan = null;
        push('% Simulator: ' + state.currentInterface + ' set to 802.1Q trunk mode.');
      }
    } else if (/^switchport trunk allowed vlan\s+.+$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        var allowed = parseAllowed(cmd.match(/vlan\s+(.+)$/i)[1]);
        state.interfaces[state.currentInterface].trunkAllowed = allowed;
        push('% Simulator: allowed VLAN list on ' + state.currentInterface + ' = ' + (allowed.join(',') || 'none') + '.');
      }
    } else if (/^switchport trunk native vlan\s+(\d+)$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        var nv = Number(cmd.match(/vlan\s+(\d+)/i)[1]);
        state.interfaces[state.currentInterface].nativeVlan = nv;
        push('% Simulator: native VLAN on ' + state.currentInterface + ' set to ' + nv + '.');
      }
    } else if (/^(?:shutdown|shut)$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        state.interfaces[state.currentInterface].shutdown = true;
        push('%LINK-5-CHANGED: Interface ' + state.currentInterface + ', changed state to administratively down.');
      }
    } else if (/^(?:no shutdown|no shut)$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        state.interfaces[state.currentInterface].shutdown = false;
        push('%LINK-3-UPDOWN: Interface ' + state.currentInterface + ', changed state to up.');
      }
    } else if (/^ip address\s+\S+\s+\S+$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        var m4 = cmd.match(/ip address\s+(\S+)\s+(\S+)/i);
        try {
          ipToInt(m4[1]);
          ipToInt(m4[2]);
          state.interfaces[state.currentInterface].ip = m4[1] + ' ' + m4[2];
          push('% Simulator: IPv4 address ' + m4[1] + ' ' + m4[2] + ' configured on ' + state.currentInterface + '.');
        } catch (err) {
          matched = false;
          push('% Bad IP address or mask: ' + err.message);
        }
      }
    } else if (/^ipv6 address\s+\S+$/i.test(cmd)) {
      if (state.mode !== 'interface' || !state.currentInterface) {
        matched = false;
        push('% Enter interface configuration mode first.');
      } else {
        state.interfaces[state.currentInterface].ipv6 = cmd.match(/ipv6 address\s+(\S+)/i)[1];
        push('% Simulator: IPv6 address configured on ' + state.currentInterface + '.');
      }
    } else if (/^router ospf\s+(\d+)$/i.test(cmd)) {
      if (!isConfigOrSub) {
        matched = false;
        push('% Enter global config mode ("configure terminal") first.');
      } else {
        state.ospfProcess = Number(cmd.match(/(\d+)$/)[1]);
        state.currentInterface = null;
        state.currentVlan = null;
        state.mode = 'router';
        push('% Simulator: OSPF process ' + state.ospfProcess + ' selected.');
      }
    } else if (/^network\s+\S+\s+\S+\s+area\s+\S+$/i.test(cmd)) {
      if (state.mode !== 'router' || !state.ospfProcess) {
        matched = false;
        push('% Enter router OSPF configuration mode first.');
      } else {
        var nm = cmd.match(/network\s+(\S+)\s+\S+\s+area\s+(\S+)/i);
        var wild = cmd.split(/\s+/)[2];
        state.ospfNetworks.push({ network: nm[1], wildcard: wild, area: nm[2] });
        push('% Simulator: OSPF network ' + nm[1] + ' ' + wild + ' area ' + nm[2] + ' added.');
      }
    } else if (/^passive-interface\s+\S+$/i.test(cmd)) {
      if (state.mode !== 'router' || !state.ospfProcess) {
        matched = false;
        push('% Enter router OSPF configuration mode first.');
      } else {
        var pi = normalizeInterface(cmd.split(/\s+/)[1]);
        if (state.passiveInterfaces.indexOf(pi) === -1) state.passiveInterfaces.push(pi);
        push('% Simulator: ' + pi + ' marked passive in OSPF.');
      }
    } else if (/^show vlan brief$/i.test(cmd)) {
      push('VLAN Name                             Status    Ports');
      push('---- -------------------------------- --------- -------------------------------');
      Object.keys(state.vlans).map(Number).sort(function (a, b) { return a - b; }).forEach(function (v) {
        var row = state.vlans[v];
        push(String(v).padEnd(5) + row.name.padEnd(33) + 'active    ' + row.ports.join(', '));
      });
    } else if (/^show interfaces trunk$/i.test(cmd)) {
      var trunks = Object.values(state.interfaces).filter(function (i) { return i.mode === 'trunk'; });
      if (!trunks.length) {
        push('% Simulator: no trunk interfaces configured.');
      } else {
        push('Port                 Mode         Encapsulation  Status        Native vlan');
        trunks.forEach(function (i) {
          push(i.name.padEnd(21) + 'on           802.1q         trunking      ' + (i.nativeVlan || 1));
        });
        push('');
        push('Port                 Vlans allowed on trunk');
        trunks.forEach(function (i) {
          push(i.name.padEnd(21) + (i.trunkAllowed.length ? i.trunkAllowed.join(',') : '1-4094'));
        });
      }
    } else if (/^show interfaces status$/i.test(cmd)) {
      var intfs = Object.values(state.interfaces);
      if (!intfs.length) {
        push('% Simulator: no interfaces touched yet.');
      } else {
        push('Port                 Name    Status       Vlan       Duplex  Speed  Type');
        intfs.forEach(function (i) {
          var st = i.shutdown ? 'disabled' : 'connected';
          var vl = i.mode === 'trunk' ? 'trunk' : String(i.vlan || '1');
          push(i.name.padEnd(21) + '--      ' + st.padEnd(13) + vl.padEnd(11) + 'a-full  a-1000 10/100/1000BaseTX');
        });
      }
    } else if (/^(?:show ip interface brief|show ip int br)$/i.test(cmd)) {
      var ifs = Object.values(state.interfaces);
      if (!ifs.length) {
        push('% Simulator: no interfaces configured yet.');
      } else {
        push('Interface              IP-Address      OK? Method Status                Protocol');
        ifs.forEach(function (i) {
          var ipOnly = i.ip ? i.ip.split(' ')[0] : 'unassigned';
          var st = i.shutdown ? 'administratively down' : 'up';
          var proto = i.shutdown ? 'down' : 'up';
          push(i.name.padEnd(23) + ipOnly.padEnd(16) + 'YES manual ' + st.padEnd(22) + proto);
        });
      }
    } else if (/^show ip ospf neighbor$/i.test(cmd)) {
      if (!state.ospfProcess || !state.ospfNetworks.length) {
        push('% Simulator: OSPF process or network statements not configured yet.');
      } else {
        var activeAreas = Array.from(new Set(state.ospfNetworks.map(function (n) { return n.area; })));
        var activeIntfs = Object.values(state.interfaces).filter(function (i) {
          return !i.shutdown && i.ip && state.passiveInterfaces.indexOf(i.name) === -1;
        });
        if (!activeIntfs.length) {
          push('% Simulator: no active non-passive IP interfaces up for OSPF neighbor discovery.');
        } else {
          push('Neighbor ID     Pri   State           Dead Time   Address         Interface');
          activeIntfs.forEach(function (i, idx) {
            var ipParts = i.ip.split(' ')[0].split('.');
            var peerIp = ipParts[0] + '.' + ipParts[1] + '.' + ipParts[2] + '.' + ((Number(ipParts[3]) % 250) + 1);
            var rid = '10.255.255.' + (idx + 2);
            push(rid.padEnd(16) + '1     FULL/DR         00:00:36    ' + peerIp.padEnd(16) + i.name + ' (Area ' + activeAreas[0] + ')');
          });
        }
      }
    } else if (/^show ip route ospf$/i.test(cmd)) {
      if (!state.ospfProcess || !state.ospfNetworks.length) {
        push('% Simulator: no OSPF routes learned.');
      } else {
        push('Codes: O - OSPF, IA - OSPF inter area');
        state.ospfNetworks.forEach(function (n, idx) {
          push('O    ' + n.network + ' (area ' + n.area + ') [110/' + (idx + 2) + '] via peer-hop, 00:00:12');
        });
      }
    } else if (/^(?:show running-config|show run)$/i.test(cmd)) {
      if (!isPrivOrAbove) {
        matched = false;
        push('% Privileged mode required. Run "enable" first.');
      } else {
        push('hostname ' + state.hostname);
        Object.keys(state.vlans).map(Number).filter(function (v) { return v !== 1; }).sort(function (a, b) { return a - b; }).forEach(function (v) {
          push('!');
          push('vlan ' + v);
          push(' name ' + state.vlans[v].name);
        });
        Object.values(state.interfaces).forEach(function (i) {
          push('!');
          push('interface ' + i.name);
          if (i.mode) push(' switchport mode ' + i.mode);
          if (i.vlan) push(' switchport access vlan ' + i.vlan);
          if (i.trunkAllowed.length) push(' switchport trunk allowed vlan ' + i.trunkAllowed.join(','));
          if (i.nativeVlan) push(' switchport trunk native vlan ' + i.nativeVlan);
          if (i.ip) push(' ip address ' + i.ip);
          if (i.ipv6) push(' ipv6 address ' + i.ipv6);
          if (i.shutdown) push(' shutdown');
        });
        if (state.ospfProcess) {
          push('!');
          push('router ospf ' + state.ospfProcess);
          state.passiveInterfaces.forEach(function (pi) { push(' passive-interface ' + pi); });
          state.ospfNetworks.forEach(function (n) { push(' network ' + n.network + ' ' + n.wildcard + ' area ' + n.area); });
        }
        push('end');
      }
    } else if (/^help$/i.test(cmd) || cmd === '?') {
      push('Supported commands: enable, disable, configure terminal, hostname <name>, vlan <id>, name <str>,');
      push('  interface <name>, switchport mode access|trunk, switchport access vlan <id>,');
      push('  switchport trunk allowed vlan <list>, switchport trunk native vlan <id>,');
      push('  ip address <ip> <mask>, shutdown, no shutdown, router ospf <pid>, network <net> <wild> area <id>,');
      push('  passive-interface <intf>, show vlan brief, show interfaces trunk, show interfaces status,');
      push('  show ip interface brief, show ip ospf neighbor, show ip route ospf, show running-config, exit, end');
    } else if (/^show /i.test(cmd)) {
      matched = false;
      push('% Simulator: unsupported show command in this educational subset.');
    } else {
      matched = false;
      push("% Invalid input detected at '^' marker. (Internal Simulator — type 'help')");
    }

    return { state: state, output: out, matched: matched, label: OUTPUT_LABEL, command: cmd };
  }

  var SIMULATOR_DEFINITIONS = [
    {
      id: 'sim-arp',
      logic: 'arpResolve',
      title: 'شبیه‌ساز ARP و تصمیم‌گیری Default Gateway',
      objective: 'مقایسه ساب‌نت مبدأ/مقصد و مشاهده تفاوت تحویل محلی با ارسال بسته به Gateway.',
      parameters: [
        { id: 'sourceIp', label: 'IP مبدأ (Source)', type: 'text', default: '192.0.2.10' },
        { id: 'targetIp', label: 'IP مقصد (Destination)', type: 'text', default: '203.0.113.10' },
        { id: 'gatewayIp', label: 'Default Gateway', type: 'text', default: '192.0.2.1' },
        { id: 'mask', label: 'پیشوند ساب‌نت (Prefix /)', type: 'number', default: 24, min: 8, max: 30 },
        { id: 'vlanId', label: 'شناسه VLAN', type: 'number', default: 10, min: 1, max: 4094 },
        { id: 'cacheHit', label: 'پاسخ در ARP Cache موجود باشد', type: 'checkbox', default: false }
      ]
    },
    {
      id: 'sim-vlan',
      logic: 'vlanForward',
      title: 'شبیه‌ساز 802.1Q VLAN و لینک Trunk',
      objective: 'بررسی برچسب‌گذاری 802.1Q، لیست Allowed VLANها و تشخیص خطای Native VLAN Mismatch.',
      parameters: [
        { id: 'sourceVlan', label: 'VLAN مبدأ', type: 'number', default: 10, min: 1, max: 4094 },
        { id: 'destinationVlan', label: 'VLAN مقصد', type: 'number', default: 10, min: 1, max: 4094 },
        { id: 'trunkAllowed', label: 'لیست مجاز Trunk (مثل 10,20,99)', type: 'text', default: '10,20,99' },
        { id: 'nativeVlan', label: 'Native VLAN در SW1', type: 'number', default: 99, min: 1, max: 4094 },
        { id: 'remoteNativeVlan', label: 'Native VLAN در SW2', type: 'number', default: 99, min: 1, max: 4094 },
        { id: 'tagNative', label: 'Tag کردن Native VLAN', type: 'checkbox', default: false }
      ]
    },
    {
      id: 'sim-ospf',
      logic: 'ospfAdjacency',
      title: 'شبیه‌ساز ماشین حالت همسایگی OSPFv2',
      objective: 'آزمایش اثر Area، تایمرهای Hello/Dead، احراز هویت و MTU بر رسیدن به حالت Full.',
      parameters: [
        { id: 'areaId', label: 'Area در R1', type: 'text', default: '0' },
        { id: 'remoteAreaId', label: 'Area در R2', type: 'text', default: '0' },
        { id: 'hello', label: 'Hello R1 (ثانیه)', type: 'number', default: 10, min: 1, max: 60 },
        { id: 'remoteHello', label: 'Hello R2 (ثانیه)', type: 'number', default: 10, min: 1, max: 60 },
        { id: 'dead', label: 'Dead R1 (ثانیه)', type: 'number', default: 40, min: 4, max: 240 },
        { id: 'remoteDead', label: 'Dead R2 (ثانیه)', type: 'number', default: 40, min: 4, max: 240 },
        { id: 'mtu', label: 'MTU در R1', type: 'number', default: 1500, min: 576, max: 9216 },
        { id: 'remoteMtu', label: 'MTU در R2', type: 'number', default: 1500, min: 576, max: 9216 },
        { id: 'auth', label: 'احراز هویت R1', type: 'select', default: 'none', options: ['none', 'simple', 'md5'] },
        { id: 'remoteAuth', label: 'احراز هویت R2', type: 'select', default: 'none', options: ['none', 'simple', 'md5'] },
        { id: 'networkType', label: 'نوع شبکه', type: 'select', default: 'broadcast', options: ['broadcast', 'point-to-point'] },
        { id: 'priority', label: 'اولویت DR در R1', type: 'number', default: 1, min: 0, max: 255 }
      ]
    }
  ];

  var LAB_PRESETS = [
    {
      id: 'lab-vlan-trunk',
      title: 'آزمایشگاه ۱: پیکربندی Access VLAN و 802.1Q Trunk',
      defaultHostname: 'SW1',
      scenario: 'در این سناریو دو VLAN مجزا (فروش و مهندسی) ایجاد کرده و پورت‌های Access و لینک Trunk بین دو سوئیچ را پیکربندی می‌کنید.',
      steps: [
        { id: 's1', title: 'ورود به مود پیکربندی و ایجاد VLAN 10 و 20', commands: ['enable', 'configure terminal', 'hostname SW1', 'vlan 10', 'name SALES', 'vlan 20', 'name ENG', 'exit'] },
        { id: 's2', title: 'اختصاص پورت Gi0/1 به VLAN 10 (Access)', commands: ['interface GigabitEthernet0/1', 'switchport mode access', 'switchport access vlan 10', 'no shutdown', 'exit'] },
        { id: 's3', title: 'پیکربندی لینک Trunk روی Gi0/24 با Native 99', commands: ['interface GigabitEthernet0/24', 'switchport mode trunk', 'switchport trunk allowed vlan 10,20,99', 'switchport trunk native vlan 99', 'end'] },
        { id: 's4', title: 'راستی‌آزمایی جدول VLAN و Trunk', commands: ['show vlan brief', 'show interfaces trunk', 'show running-config'] }
      ]
    },
    {
      id: 'lab-ospf-single-area',
      title: 'آزمایشگاه ۲: راه‌اندازی OSPFv2 Single-Area روی روتر',
      defaultHostname: 'R1',
      scenario: 'آدرس‌دهی اینترفیس‌های WAN و LAN روی روتر R1، فعال‌سازی OSPF Process 1 در Area 0 و تنظیم Passive Interface سمت کاربران.',
      steps: [
        { id: 'o1', title: 'آدرس‌دهی اینترفیس‌های روتر', commands: ['enable', 'configure terminal', 'hostname R1', 'interface GigabitEthernet0/0', 'ip address 192.0.2.1 255.255.255.252', 'no shutdown', 'interface GigabitEthernet0/1', 'ip address 10.10.10.1 255.255.255.0', 'no shutdown', 'exit'] },
        { id: 'o2', title: 'فعال‌سازی OSPF و معرفی شبکه‌ها', commands: ['router ospf 1', 'passive-interface GigabitEthernet0/1', 'network 192.0.2.0 0.0.0.3 area 0', 'network 10.10.10.0 0.0.0.255 area 0', 'end'] },
        { id: 'o3', title: 'بررسی همسایگی و مسیرهای OSPF', commands: ['show ip interface brief', 'show ip ospf neighbor', 'show ip route ospf'] }
      ]
    },
    {
      id: 'lab-interface-tshoot',
      title: 'آزمایشگاه ۳: عیب‌یابی پورت خاموش (Shutdown) در روتر',
      defaultHostname: 'R-EDGE',
      scenario: 'اینترفیس Gi0/0 دارای IP است اما به‌دلیل وضعیت administratively down ارتباط قطع است؛ وضعیت را بررسی و رفع کنید.',
      steps: [
        { id: 't1', title: 'ایجاد وضعیت خطای اولیه', commands: ['enable', 'configure terminal', 'hostname R-EDGE', 'interface GigabitEthernet0/0', 'ip address 198.51.100.1 255.255.255.252', 'shutdown', 'end'] },
        { id: 't2', title: 'بررسی خطا در جدول رابط‌ها', commands: ['show ip interface brief', 'show interfaces status'] },
        { id: 't3', title: 'رفع خطا با no shutdown و تایید نهایی', commands: ['configure terminal', 'interface GigabitEthernet0/0', 'no shutdown', 'end', 'show ip interface brief'] }
      ]
    }
  ];

  return {
    OUTPUT_LABEL: OUTPUT_LABEL,
    SIMULATOR_DEFINITIONS: SIMULATOR_DEFINITIONS,
    LAB_PRESETS: LAB_PRESETS,
    ipToInt: ipToInt,
    maskInt: maskInt,
    sameSubnet: sameSubnet,
    macFor: macFor,
    parseAllowed: parseAllowed,
    arpResolve: arpResolve,
    vlanForward: vlanForward,
    ospfAdjacency: ospfAdjacency,
    createLabState: createLabState,
    runLabCommand: runLabCommand,
    normalizeInterface: normalizeInterface
  };
});
