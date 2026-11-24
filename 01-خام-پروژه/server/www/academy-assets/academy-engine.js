/* FAM Academy v2 — pure educational logic engine.
 * No DOM, no network, no device access. Exposed as window.FAMAcademyEngine
 * in the browser and as a CommonJS module for Node-based contract tests.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.FAMAcademyEngine = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var OUTPUT_LABEL = 'Sample / Simulated — Internal Simulator';
  var ENGINE_FUNCTIONS = ['arpResolve', 'vlanForward', 'ospfAdjacency'];

  function ipToInt(ip) {
    var parts = String(ip || '').split('.');
    if (parts.length !== 4) throw new Error('IPv4 address must contain four octets');
    var n = 0;
    for (var i = 0; i < 4; i += 1) {
      var v = Number(parts[i]);
      if (!Number.isInteger(v) || v < 0 || v > 255) throw new Error('IPv4 octet out of range');
      n = ((n << 8) + v) >>> 0;
    }
    return n >>> 0;
  }

  function maskInt(prefix) {
    var p = Number(prefix);
    if (!Number.isInteger(p) || p < 0 || p > 32) throw new Error('Prefix must be between 0 and 32');
    if (p === 0) return 0;
    return (0xffffffff << (32 - p)) >>> 0;
  }

  function sameSubnet(a, b, prefix) {
    var m = maskInt(prefix);
    return ((ipToInt(a) & m) >>> 0) === ((ipToInt(b) & m) >>> 0);
  }

  function macFor(ip) {
    var last = ipToInt(ip) & 255;
    var hex = last.toString(16).padStart(2, '0').toUpperCase();
    return '02:00:00:00:00:' + hex;
  }

  function bool(v) {
    return v === true || v === 'true' || v === 'on' || v === 1 || v === '1';
  }

  function num(v, fallback) {
    var n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  }

  function arpResolve(params) {
    params = params || {};
    try {
      var sourceIp = String(params.sourceIp || '192.0.2.10');
      var targetIp = String(params.targetIp || '192.0.2.20');
      var gatewayIp = String(params.gatewayIp || '192.0.2.1');
      var prefix = num(params.mask, 24);
      var cacheHit = bool(params.cacheHit);
      var vlanId = num(params.vlanId, 10);
      ipToInt(sourceIp); ipToInt(targetIp); ipToInt(gatewayIp); maskInt(prefix);
      var local = sameSubnet(sourceIp, targetIp, prefix);
      var arpTargetIp = local ? targetIp : gatewayIp;
      var srcMac = macFor(sourceIp);
      var targetMac = macFor(arpTargetIp);
      var steps = [];
      var table = [];
      var t = 0;
      function add(title, from, to, protocol, message, detail, size) {
        var row = { index: steps.length + 1, time: (t / 1000).toFixed(3) + 's', from: from, to: to, protocol: protocol, message: message, detail: detail, size: size, title: title };
        steps.push(row); table.push(row); t += 12;
      }
      add('بررسی سابنت', sourceIp, '-', 'IPv4', 'Compare ' + sourceIp + '/' + prefix + ' with ' + targetIp, local ? 'مقصد در همان سابنت است؛ ARP برای IP مقصد ساخته میشود.' : 'مقصد خارج از سابنت است؛ ARP باید MAC Default Gateway را پیدا کند.', '0 B');
      add('تصمیم مقصد ARP', sourceIp, arpTargetIp, 'ARP', 'Resolve ' + arpTargetIp, local ? 'Target IP = ' + targetIp : 'Next-hop IP = ' + gatewayIp + '؛ IP مقصد نهایی همچنان ' + targetIp + ' باقی میماند.', '28 B');
      if (cacheHit) {
        add('استفاده از ARP Cache', sourceIp, arpTargetIp, 'ARP', 'Cache hit for ' + arpTargetIp, 'ورودی از قبل وجود دارد؛ هیچ Broadcast ارسال نمیشود. MAC = ' + targetMac, '0 B');
      } else {
        add('ارسال ARP Request', sourceIp, 'Broadcast', 'ARP', 'Who has ' + arpTargetIp + '? Tell ' + sourceIp, 'Ethernet dst = ff:ff:ff:ff:ff:ff؛ سوئیچ فریم را در VLAN ' + vlanId + ' Flood میکند.', '42 B');
        add('دریافت ARP Reply', arpTargetIp, sourceIp, 'ARP', arpTargetIp + ' is at ' + targetMac, 'پاسخ معمولاً Unicast است و Cache فرستنده بهروز میشود.', '42 B');
      }
      add('ساخت Frame نهایی', sourceIp, targetIp, 'IPv4/Ethernet', local ? 'Frame to ' + targetIp : 'Frame to gateway, IP dst ' + targetIp, 'Ethernet dst = ' + targetMac + '؛ Ethernet src = ' + srcMac + '؛ IP Source/Destination بدون تغییر باقی میماند.', '98 B');
      return {
        ok: true, logic: 'arpResolve', label: OUTPUT_LABEL, decision: local ? 'Local delivery' : 'Remote delivery via gateway',
        summary: local
          ? 'مقصد در همان /' + prefix + ' قرار دارد؛ ARP مستقیماً MAC ' + targetIp + ' را کشف کرد.'
          : 'مقصد خارج از سابنت است؛ ARP برای Gateway ' + gatewayIp + ' انجام شد و بسته IP همچنان به ' + targetIp + ' آدرسدهی شده است.',
        params: { sourceIp: sourceIp, targetIp: targetIp, gatewayIp: gatewayIp, mask: prefix, cacheHit: cacheHit, vlanId: vlanId },
        steps: steps, table: table,
        warnings: cacheHit ? ['Cache Hit مانع تولید Broadcast شد؛ برای دیدن Request/Reply گزینه Cache را خاموش کنید.'] : ['Proxy ARP و Gratuitous ARP در این مدل آموزشی پیادهسازی نشدهاند.'],
        limitations: ['مدل فقط IPv4 و prefix /8 تا /30 را پوشش میدهد.', 'MACها و زمانها مثال آموزشی هستند، نه خروجی دستگاه واقعی.']
      };
    } catch (e) {
      return { ok: false, logic: 'arpResolve', label: OUTPUT_LABEL, error: String(e.message || e), steps: [], table: [], warnings: ['ورودی IPv4 یا Prefix نامعتبر است.'] };
    }
  }

  function parseAllowed(text) {
    return String(text || '')
      .split(/[,\s]+/)
      .map(function (x) { return Number(x.trim()); })
      .filter(function (x) { return Number.isInteger(x) && x >= 1 && x <= 4094; });
  }

  function vlanForward(params) {
    params = params || {};
    var sourceVlan = num(params.sourceVlan, 10);
    var destinationVlan = num(params.destinationVlan, sourceVlan);
    var nativeVlan = num(params.nativeVlan, 99);
    var remoteNativeVlan = num(params.remoteNativeVlan, nativeVlan);
    var allowed = parseAllowed(params.trunkAllowed);
    var tagNative = bool(params.tagNative);
    var allowedSet = new Set(allowed);
    var warnings = [];
    var steps = [];
    var table = [];
    var dropReason = null;
    function add(title, from, to, protocol, message, detail, size) {
      var row = { index: steps.length + 1, time: ((steps.length * 0.012).toFixed(3)) + 's', from: from, to: to, protocol: protocol, message: message, detail: detail, size: size, title: title };
      steps.push(row); table.push(row);
    }
    add('دریافت فریم Access', 'Host A', 'SW1', 'Ethernet', 'Untagged frame in VLAN ' + sourceVlan, 'پورت Access فریم بدون 802.1Q Tag دریافت میکند و سوئیچ آن را به VLAN ' + sourceVlan + ' نگاشت میکند.', '64 B');
    var allowedOk = allowedSet.has(sourceVlan);
    add('بررسی Allowed List', 'SW1', 'Trunk', '802.1Q', allowedOk ? 'VLAN ' + sourceVlan + ' allowed' : 'VLAN ' + sourceVlan + ' NOT allowed', allowedOk ? 'Allowed VLANs: ' + (allowed.join(',') || 'none') : 'فریم پیش از ورود به Trunk حذف میشود.', allowedOk ? '0 B' : 'DROPPED');
    if (!allowedOk) dropReason = 'VLAN ' + sourceVlan + ' در Allowed VLAN List وجود ندارد.';
    var isNative = sourceVlan === nativeVlan;
    var tagged = !isNative || tagNative;
    add('تصمیم Tag', 'SW1', 'SW2', '802.1Q', tagged ? 'Tagged VID ' + sourceVlan : 'Untagged (native VLAN ' + nativeVlan + ')', tagged ? 'فیلد VID=' + sourceVlan + ' به Frame اضافه میشود.' : 'بهطور پیشفرض Native VLAN بدون Tag حمل میشود.', tagged ? '68 B' : '64 B');
    if (isNative && !tagNative && remoteNativeVlan !== nativeVlan) {
      warnings.push('Native VLAN Mismatch: سر مقصد فریم untagged را به VLAN ' + remoteNativeVlan + ' تفسیر میکند، در حالی که مبدأ VLAN ' + nativeVlan + ' بوده است.');
      dropReason = 'تفسیر ناهمساز Native VLAN؛ تحویل امن لغو شد.';
    }
    if (isNative && tagNative) warnings.push('Tag کردن Native VLAN فعال است؛ این کار از ابهام ناشی از untagged frame جلوگیری میکند.');
    var l2Delivery = allowedOk && !dropReason && sourceVlan === destinationVlan;
    add('عبور از Trunk', 'SW1', 'SW2', '802.1Q', allowedOk ? 'Frame crosses trunk' : 'Frame discarded', allowedOk ? 'لینک فیزیکی چند VLAN را با برچسب/استثنای Native حمل میکند.' : dropReason, allowedOk ? '68 B' : 'DROPPED');
    add('تحویل در مقصد', 'SW2', 'Host B', 'Ethernet', l2Delivery ? 'Delivered in VLAN ' + destinationVlan : 'No L2 delivery', l2Delivery ? 'مقصد در همان VLAN است؛ Frame بدون Tag به پورت Access تحویل میشود.' : (sourceVlan !== destinationVlan ? 'مقصد در VLAN دیگری است؛ بدون Inter-VLAN Routing تحویل لایه ۲ انجام نمیشود.' : dropReason), l2Delivery ? '64 B' : 'DROPPED');
    if (sourceVlan !== destinationVlan) warnings.push('VLAN مبدأ و مقصد متفاوتاند؛ برای ارتباط آنها به SVI، Router-on-a-Stick یا Routing لایه ۳ نیاز است.');
    return {
      ok: true, logic: 'vlanForward', label: OUTPUT_LABEL,
      decision: l2Delivery ? 'Delivered' : 'Dropped / needs routing',
      summary: l2Delivery
        ? 'فریم VLAN ' + sourceVlan + (tagged ? ' بهصورت Tagged' : ' بهصورت Untagged/Native') + ' از Trunk عبور کرد و در همان VLAN تحویل شد.'
        : 'تحویل لایه ۲ انجام نشد: ' + (dropReason || 'مبدأ و مقصد در VLANهای متفاوتی قرار دارند.'),
      params: { sourceVlan: sourceVlan, destinationVlan: destinationVlan, nativeVlan: nativeVlan, remoteNativeVlan: remoteNativeVlan, allowed: allowed, tagNative: tagNative },
      steps: steps, table: table, warnings: warnings,
      limitations: ['STP، DTP، VTP و QoS روی Trunk مدل نشدهاند.', 'فقط یک لینک Trunk و یک Broadcast Domain بررسی میشود.']
    };
  }

  function ospfAdjacency(params) {
    params = params || {};
    var area = String(params.areaId || '0');
    var remoteArea = String(params.remoteAreaId || area);
    var hello = num(params.hello, 10), remoteHello = num(params.remoteHello, hello);
    var dead = num(params.dead, 40), remoteDead = num(params.remoteDead, dead);
    var auth = String(params.auth || 'none'), remoteAuth = String(params.remoteAuth || auth);
    var mtu = num(params.mtu, 1500), remoteMtu = num(params.remoteMtu, mtu);
    var networkType = String(params.networkType || 'broadcast');
    var priority = num(params.priority, 1);
    var mismatches = [];
    if (area !== remoteArea) mismatches.push('Area ID (' + area + ' vs ' + remoteArea + ')');
    if (hello !== remoteHello) mismatches.push('Hello Interval (' + hello + 's vs ' + remoteHello + 's)');
    if (dead !== remoteDead) mismatches.push('Dead Interval (' + dead + 's vs ' + remoteDead + 's)');
    if (auth !== remoteAuth) mismatches.push('Authentication (' + auth + ' vs ' + remoteAuth + ')');
    var mtuMismatch = mtu !== remoteMtu;
    if (mtuMismatch) mismatches.push('MTU (' + mtu + ' vs ' + remoteMtu + ')');
    var sequence = ['Down', 'Init', '2-Way', 'ExStart', 'Exchange', 'Loading', 'Full'];
    var stopIndex = sequence.length - 1;
    var finalState = 'Full';
    var reason = 'همه پارامترها سازگاراند و LSDB همزمان شد.';
    if (mismatches.length) {
      if (area !== remoteArea || hello !== remoteHello || dead !== remoteDead || auth !== remoteAuth) stopIndex = 1;
      else stopIndex = 3;
      finalState = sequence[stopIndex];
      reason = 'عدم تطابق پارامترها: ' + mismatches.join('، ') + '.';
    } else if (networkType === 'broadcast' && priority === 0) {
      stopIndex = 2;
      finalState = '2-Way';
      reason = 'روتر با Priority=0 فقط DROther است؛ با DR/BDR به Full میرسد ولی با DROther دیگر تا 2-Way باقی میماند.';
    }
    var steps = [];
    var table = [];
    var detailByState = {
      'Down': 'هنوز Hello معتبری دریافت نشده است.',
      'Init': 'Hello دریافت شد ولی Router ID محلی در Hello طرف مقابل دیده نشد.',
      '2-Way': 'ارتباط دوسویه برقرار شد؛ در شبکه Broadcast انتخاب DR/BDR انجام میگیرد.',
      'ExStart': 'روترها Master/Slave و شماره توالی DBD را توافق میکنند.',
      'Exchange': 'بستههای DBD مبادله و LSA Headerها مقایسه میشوند.',
      'Loading': 'درخواست LSR و ارسال LSU/LSAck برای پرکردن LSDB انجام میشود.',
      'Full': 'همسایگی adjacency کامل شد و SPF میتواند روی LSDB اجرا شود.'
    };
    for (var i = 0; i <= stopIndex; i += 1) {
      var state = sequence[i];
      var row = {
        index: i + 1, time: (i * 0.01).toFixed(3) + 's', from: 'R1', to: 'R2', protocol: 'OSPF',
        message: state, detail: detailByState[state], size: state === 'Down' ? '0 B' : 'Hello/DBD', title: state
      };
      steps.push(row); table.push(row);
    }
    if (stopIndex < sequence.length - 1) {
      var warn = { index: steps.length + 1, time: ((stopIndex + 1) * 0.01).toFixed(3) + 's', from: 'R1', to: 'R2', protocol: 'OSPF', message: 'STOP at ' + finalState, detail: reason, size: '—', title: 'توقف' };
      steps.push(warn); table.push(warn);
    }
    return {
      ok: true, logic: 'ospfAdjacency', label: OUTPUT_LABEL,
      decision: finalState,
      summary: finalState === 'Full'
        ? 'همسایگی OSPF به Full رسید؛ Area، Timers، Authentication و MTU سازگار بودند.'
        : 'همسایگی در حالت ' + finalState + ' متوقف شد. ' + reason,
      params: { areaId: area, remoteAreaId: remoteArea, hello: hello, remoteHello: remoteHello, dead: dead, remoteDead: remoteDead, auth: auth, remoteAuth: remoteAuth, mtu: mtu, remoteMtu: remoteMtu, networkType: networkType, priority: priority },
      finalState: finalState, steps: steps, table: table,
      warnings: mismatches.length ? mismatches : (priority === 0 ? ['Priority=0 یعنی روتر در انتخاب DR شرکت نمیکند.'] : []),
      limitations: ['مدل آموزشی OSPFv2 است؛ LSA flooding کامل، NBMA و OSPFv3 پیادهسازی نشدهاند.', 'انتخاب DR/BDR بهصورت ساده و فقط بر اساس Priority مدل شده است.']
    };
  }

  function evaluateQuiz(lesson, answers) {
    var quiz = (lesson && lesson.quiz) || [];
    var list = Array.isArray(answers) ? answers : [];
    var details = [];
    var correct = 0;
    for (var i = 0; i < quiz.length; i += 1) {
      var q = quiz[i], given = list[i], good = Number.isInteger(given) && given >= 0 && given < q.options.length && given === q.answerIndex;
      if (good) correct += 1;
      details.push({ id: q.id, prompt: q.prompt, given: given, correctIndex: q.answerIndex, correct: good, explanation: q.explanation, options: q.options });
    }
    var total = quiz.length;
    return { ok: true, total: total, correct: correct, score: total ? Math.round((correct * 100) / total) : 0, details: details, label: OUTPUT_LABEL };
  }

  function createLabState(lab) {
    return {
      labId: lab && lab.id ? lab.id : 'lab', mode: 'user', hostname: '', currentInterface: null, currentVlan: null,
      interfaces: {}, vlans: {}, ospfNetworks: [], ospfProcess: null, passiveInterfaces: [],
      executed: [], label: OUTPUT_LABEL, realDeviceConnection: false
    };
  }

  function normalizeInterface(name) {
    var n = String(name || '').trim();
    if (/^gi\d+\/\d+$/i.test(n)) return 'GigabitEthernet' + n.slice(2);
    if (/^fa\d+\/\d+$/i.test(n)) return 'FastEthernet' + n.slice(2);
    return n;
  }

  function runLabCommand(state, raw) {
    var cmd = String(raw || '').trim().replace(/\s+/g, ' ');
    var out = [];
    var matched = true;
    function push(line) { out.push(String(line)); }
    if (!cmd) return { state: state, output: [], matched: true, label: OUTPUT_LABEL };
    state.executed.push(cmd);
    if (cmd === 'enable') {
      state.mode = 'privileged'; push('% Simulator: privileged EXEC mode (no password configured).');
    } else if (cmd === 'disable') {
      state.mode = 'user'; push('% Simulator: returned to user EXEC mode.');
    } else if (cmd === 'configure terminal' || cmd === 'conf t') {
      if (state.mode !== 'privileged') push('% Simulator: enter privileged mode with "enable" first.');
      else { state.mode = 'config'; push('Enter configuration commands, one per line. End with CNTL/Z.'); }
    } else if (cmd === 'end') {
      state.mode = 'privileged'; state.currentInterface = null; state.currentVlan = null; push('% Simulator: configuration mode exited.');
    } else if (cmd === 'exit') {
      if (state.mode === 'interface' || state.mode === 'vlan' || state.mode === 'router') { state.mode = 'config'; state.currentInterface = null; state.currentVlan = null; }
      else if (state.mode === 'config') state.mode = 'privileged';
      else if (state.mode === 'privileged') state.mode = 'user';
      push('% Simulator: mode is now ' + state.mode + '.');
    } else if (/^hostname\s+\S+$/i.test(cmd)) {
      state.hostname = cmd.split(/\s+/)[1]; push('% Simulator: hostname set to ' + state.hostname + '.');
    } else if (/^vlan\s+\d+$/i.test(cmd)) {
      var vid = Number(cmd.split(/\s+/)[1]); state.vlans[vid] = state.vlans[vid] || { id: vid, name: 'VLAN' + String(vid).padStart(4, '0'), ports: [] }; state.currentVlan = vid; state.mode = 'vlan'; push('% Simulator: VLAN ' + vid + ' created/selected.');
    } else if (/^name\s+\S+/i.test(cmd) && state.mode === 'vlan' && state.currentVlan) {
      state.vlans[state.currentVlan].name = cmd.replace(/^name\s+/i, '').trim(); push('% Simulator: VLAN name updated.');
    } else if (/^interface\s+\S+$/i.test(cmd)) {
      var iface = normalizeInterface(cmd.split(/\s+/)[1]); state.currentInterface = iface; state.interfaces[iface] = state.interfaces[iface] || { name: iface, mode: '', vlan: null, ip: null, shutdown: false, trunkAllowed: [], nativeVlan: null }; state.mode = 'interface'; push('% Simulator: interface ' + iface + ' selected.');
    } else if (/^switchport mode access$/i.test(cmd) && state.mode === 'interface') {
      state.interfaces[state.currentInterface].mode = 'access'; push('% Simulator: port forced to access mode.');
    } else if (/^switchport access vlan\s+\d+$/i.test(cmd) && state.mode === 'interface') {
      var av = Number(cmd.match(/vlan\s+(\d+)/i)[1]); state.interfaces[state.currentInterface].vlan = av; state.vlans[av] = state.vlans[av] || { id: av, name: 'VLAN' + String(av).padStart(4, '0'), ports: [] }; state.vlans[av].ports.push(state.currentInterface); push('% Simulator: interface assigned to VLAN ' + av + '.');
    } else if (/^switchport mode trunk$/i.test(cmd) && state.mode === 'interface') {
      state.interfaces[state.currentInterface].mode = 'trunk'; push('% Simulator: port forced to 802.1Q trunk mode.');
    } else if (/^switchport trunk allowed vlan\s+.+$/i.test(cmd) && state.mode === 'interface') {
      var allowed = parseAllowed(cmd.match(/vlan\s+(.+)$/i)[1]); state.interfaces[state.currentInterface].trunkAllowed = allowed; push('% Simulator: allowed VLAN list = ' + (allowed.join(',') || 'none') + '.');
    } else if (/^switchport trunk native vlan\s+\d+$/i.test(cmd) && state.mode === 'interface') {
      state.interfaces[state.currentInterface].nativeVlan = Number(cmd.match(/vlan\s+(\d+)/i)[1]); push('% Simulator: native VLAN set.');
    } else if (/^no shutdown$/i.test(cmd) && state.mode === 'interface') {
      state.interfaces[state.currentInterface].shutdown = false; push('% Simulator: interface administratively up.');
    } else if (/^ip address\s+\S+\s+\S+$/i.test(cmd) && state.mode === 'interface') {
      var m = cmd.match(/ip address\s+(\S+)\s+(\S+)/i); state.interfaces[state.currentInterface].ip = m[1] + ' ' + m[2]; push('% Simulator: IPv4 address configured.');
    } else if (/^ipv6 address\s+\S+$/i.test(cmd) && state.mode === 'interface') {
      state.interfaces[state.currentInterface].ip = cmd.match(/ipv6 address\s+(\S+)/i)[1]; push('% Simulator: IPv6 address configured.');
    } else if (/^router ospf\s+\d+$/i.test(cmd)) {
      state.ospfProcess = Number(cmd.match(/(\d+)$/)[1]); state.mode = 'router'; push('% Simulator: OSPF process ' + state.ospfProcess + ' selected.');
    } else if (/^network\s+\S+\s+\S+\s+area\s+\S+$/i.test(cmd) && state.mode === 'router') {
      var nm = cmd.match(/network\s+(\S+)\s+(\S+)\s+area\s+(\S+)/i); state.ospfNetworks.push({ network: nm[1], wildcard: nm[2], area: nm[3] }); push('% Simulator: OSPF network statement added for area ' + nm[3] + '.');
    } else if (/^passive-interface\s+\S+$/i.test(cmd) && state.mode === 'router') {
      state.passiveInterfaces.push(normalizeInterface(cmd.split(/\s+/)[1])); push('% Simulator: interface marked passive.');
    } else if (/^show vlan brief$/i.test(cmd)) {
      push('VLAN Name                             Status    Ports');
      push('---- -------------------------------- --------- -------------------------------');
      push('1    default                          active');
      Object.keys(state.vlans).map(Number).sort(function (a, b) { return a - b; }).forEach(function (v) {
        var row = state.vlans[v]; push(String(v).padEnd(5) + row.name.padEnd(33) + 'active    ' + (row.ports.join(', ') || ''));
      });
    } else if (/^show interfaces trunk$/i.test(cmd)) {
      push('Port        Mode         Encapsulation  Status        Native vlan');
      var trunks = Object.values(state.interfaces).filter(function (i) { return i.mode === 'trunk'; });
      if (!trunks.length) push('% Simulator: no trunk interfaces configured.');
      trunks.forEach(function (i) { push(i.name.padEnd(12) + 'on           802.1q         trunking      ' + (i.nativeVlan || 1)); });
      push('Port        Vlans allowed on trunk');
      trunks.forEach(function (i) { push(i.name.padEnd(12) + (i.trunkAllowed.join(',') || 'none')); });
    } else if (/^show interfaces status$/i.test(cmd)) {
      push('Port      Name  Status       Vlan  Duplex  Speed  Type');
      Object.values(state.interfaces).forEach(function (i) { push(i.name.padEnd(10) + '--    connected    ' + String(i.vlan || (i.mode === 'trunk' ? 'trunk' : '1')).padEnd(6) + 'a-full  a-1000  10/100/1000BaseTX'); });
    } else if (/^show ip interface brief$/i.test(cmd)) {
      push('Interface       IP-Address   OK? Method Status                Protocol');
      Object.values(state.interfaces).forEach(function (i) { push(i.name.padEnd(16) + (i.ip ? i.ip.split(' ')[0] : 'unassigned').padEnd(13) + 'YES  manual  up                    up'); });
    } else if (/^show ip ospf neighbor$/i.test(cmd)) {
      if (!state.ospfNetworks.length) push('% Simulator: no OSPF network statements yet.');
      else if (state.ospfNetworks.some(function (n) { return n.area !== '0'; })) push('% Simulator: Area mismatch detected; adjacency not FULL.');
      else push('Neighbor ID  Pri  State      Dead Time  Address      Interface');
      if (state.ospfNetworks.length && state.ospfNetworks.every(function (n) { return n.area === '0'; })) push('203.0.113.1    1   FULL/DR    00:00:34   192.0.2.2    GigabitEthernet0/0');
    } else if (/^show ip route ospf$/i.test(cmd)) {
      if (!state.ospfNetworks.length) push('% Simulator: no OSPF routes learned.');
      else push('O    203.0.113.0/24 [110/2] via 192.0.2.2, 00:00:12, GigabitEthernet0/0');
    } else if (/^show running-config$/i.test(cmd)) {
      push('hostname ' + (state.hostname || 'Switch'));
      Object.values(state.interfaces).forEach(function (i) { push('interface ' + i.name); if (i.mode) push(' switchport mode ' + i.mode); if (i.vlan) push(' switchport access vlan ' + i.vlan); if (i.ip) push(' ip address ' + i.ip); });
      if (state.ospfProcess) { push('router ospf ' + state.ospfProcess); state.ospfNetworks.forEach(function (n) { push(' network ' + n.network + ' ' + n.wildcard + ' area ' + n.area); }); }
    } else if (/^show /i.test(cmd)) {
      push('% Simulator: unsupported show command in this educational subset.');
      matched = false;
    } else {
      push("% Invalid input detected at '^' marker. (Simulator)");
      matched = false;
    }
    return { state: state, output: out, matched: matched, label: OUTPUT_LABEL, command: cmd };
  }

  return {
    OUTPUT_LABEL: OUTPUT_LABEL,
    ENGINE_FUNCTIONS: ENGINE_FUNCTIONS,
    ipToInt: ipToInt,
    maskInt: maskInt,
    sameSubnet: sameSubnet,
    macFor: macFor,
    arpResolve: arpResolve,
    vlanForward: vlanForward,
    ospfAdjacency: ospfAdjacency,
    evaluateQuiz: evaluateQuiz,
    createLabState: createLabState,
    runLabCommand: runLabCommand,
    normalizeInterface: normalizeInterface
  };
});
