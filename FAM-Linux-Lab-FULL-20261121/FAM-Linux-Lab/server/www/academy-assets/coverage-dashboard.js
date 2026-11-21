(() => {
  'use strict';
  window.FamCoverageDashboard = {
    computeStats(kb) {
      const cmds = kb?.commands || [];
      return {
        total: cmds.length,
        documentationVerified: cmds.filter(c => c.documentationVerified).length,
        simulatorImplemented: cmds.filter(c => c.simulatorImplemented).length,
        simulatorTested: cmds.filter(c => c.simulatorTested).length,
        realDeviceTested: cmds.filter(c => c.realDeviceTested).length,
        IMPLEMENTED: cmds.filter(c => c.status === 'IMPLEMENTED').length,
        READ_ONLY: cmds.filter(c => c.status === 'READ_ONLY').length,
        HELP_ONLY: cmds.filter(c => c.status === 'HELP_ONLY').length,
        NOT_IMPLEMENTED: cmds.filter(c => c.status === 'NOT_IMPLEMENTED').length,
        UNSUPPORTED: cmds.filter(c => c.status === 'UNSUPPORTED').length,
        PLACEHOLDER: cmds.filter(c => c.status === 'PLACEHOLDER').length
      };
    },
    render(container, kb) {
      const s = this.computeStats(kb);
      const cmds = kb?.commands || [];
      container.innerHTML = `
        <section class="hero">
          <h1>Command Coverage Dashboard</h1>
          <p>گزارش واقعی پوشش دستورات از منبع واحد kb-ios.json (آخرین بررسی: ${kb?.meta?.lastChecked || '-'})</p>
        </section>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:10px;margin-bottom:20px">
          <div class="card"><h3>${s.total}</h3><p>Total Commands</p></div>
          <div class="card"><h3>${s.documentationVerified}</h3><p>Doc Verified</p></div>
          <div class="card"><h3 style="color:var(--ok)">${s.simulatorImplemented}</h3><p>Sim Implemented</p></div>
          <div class="card"><h3 style="color:var(--ok)">${s.simulatorTested}</h3><p>Sim Tested</p></div>
          <div class="card"><h3>${s.realDeviceTested}</h3><p>Real Device Tested</p></div>
          <div class="card"><h3 style="color:var(--accent)">${s.READ_ONLY}</h3><p>Read Only</p></div>
          <div class="card"><h3>${s.HELP_ONLY}</h3><p>Help Only</p></div>
          <div class="card"><h3 style="color:var(--warn)">${s.NOT_IMPLEMENTED}</h3><p>Not Implemented</p></div>
          <div class="card"><h3 style="color:var(--err)">${s.UNSUPPORTED}</h3><p>Unsupported</p></div>
          <div class="card"><h3 style="color:var(--warn)">${s.PLACEHOLDER}</h3><p>Placeholder</p></div>
        </div>
        <div class="course-box" style="overflow-x:auto">
          <table style="width:100%;border-collapse:collapse;font-size:12px;text-align:right">
            <thead>
              <tr style="background:var(--panel2);border-bottom:1px solid var(--border)">
                <th style="padding:10px">دستور</th><th style="padding:10px">دسته</th><th style="padding:10px">خانواده</th><th style="padding:10px">Mode</th><th style="padding:10px">وضعیت</th>
              </tr>
            </thead>
            <tbody>
              ${cmds.map(c => `
                <tr style="border-bottom:1px solid var(--border)">
                  <td style="padding:8px 10px;font-family:var(--mono);direction:ltr;text-align:left">${c.canonical}</td>
                  <td style="padding:8px 10px">${c.category}</td>
                  <td style="padding:8px 10px">${c.deviceFamily} (${c.minVersion})</td>
                  <td style="padding:8px 10px">${c.modes.join(', ')}</td>
                  <td style="padding:8px 10px"><span class="badge">${c.status}</span></td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>`;
    }
  };
})();
