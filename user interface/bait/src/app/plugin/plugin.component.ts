import {Component, ViewChild} from '@angular/core';

@Component({
  selector: 'app-plugin',
  templateUrl: './plugin.component.html',
  styleUrls: ['./plugin.component.scss']
})
export class PluginComponent {

  @ViewChild('fileInput') fileInput: any;

  plugin_opened: boolean | undefined = undefined;
  plugin_closed: boolean | undefined = undefined;
  messageText: string = '';
  imageSrc: string | ArrayBuffer | null = '';

  constructor() {
  }

  ngOnInit(): void {
    document?.querySelector('.message_input')?.addEventListener('keydown', (event) => {
      if ((event as KeyboardEvent).key == 'Enter') {
        event.preventDefault();
        this.sendMessage(this.messageText);
      }
    });
  }

  onImageSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => this.imageSrc = reader.result;
      reader.readAsDataURL(file);
    }
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

  triggerFileInput(): void {
    if (this.imageSrc) {
      this.imageSrc = null;
    } else {
      this.fileInput.nativeElement.click();
    }
  }

  sendMessage(message: string): void {
    console.log('Text:', message);
    console.log('Image Data:', this.imageSrc);

    this.messageText = '';
    this.imageSrc = null;
  }
}
