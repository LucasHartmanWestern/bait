import { Component } from '@angular/core';

@Component({
  selector: 'app-plugin',
  templateUrl: './plugin.component.html',
  styleUrls: ['./plugin.component.scss']
})
export class PluginComponent {

  plugin_opened: boolean | undefined = undefined;
  plugin_closed: boolean | undefined = undefined;

  constructor() {
  }

  toggleFab(): void {
    if (this.plugin_opened == undefined) {
      this.plugin_opened = true;
      this.plugin_closed = false;
    } else {
      this.plugin_opened = !this.plugin_opened;
      this.plugin_closed = !this.plugin_closed;
    }
  }

}
