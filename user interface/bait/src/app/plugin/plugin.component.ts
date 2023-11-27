import { Component, ViewChild } from '@angular/core';
import { MessageService } from "../services/message.service";
import {load} from "@angular-devkit/build-angular/src/utils/server-rendering/esm-in-memory-file-loader";

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
  loading: boolean = false;

  messages: {role: string, content: string}[] = [
    { role: 'user', content: 'I am doing a project for school, can you act as a representative for Bell support when I send you questions and images pertaining to Bell.' },
    { role: 'system', content: 'Understood, please proceed.' }
  ];

  constructor(private messageService: MessageService) {
  }

  ngOnInit(): void {
    document?.querySelector('.message_input')?.addEventListener('keydown', (event) => {
      if ((event as KeyboardEvent).key == 'Enter') {
        event.preventDefault();
        this.sendMessage(this.messageText);
      }
    });

    setInterval(() => {
      let loading = document.querySelector('.loading');
      if (loading) {
        let dots = loading.textContent;
        switch(dots) {
          case '':
            loading.textContent = '.';
            break;
          case '.':
            loading.textContent = '..';
            break;
          case '..':
            loading.textContent = '...';
            break;
          case '...':
            loading.textContent = '';
            break;
        }
      }
    }, 250);
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

    this.messages.push({role: 'user', content: message})

    this.loading = true;
    this.messageService.sendMessage(this.messages, this.imageSrc).subscribe(res => {
      this.loading = false;
      this.messages.push({role: 'system', content: res?.response})
    }, error => {
      this.loading = false;
      console.log(error);
    });

    this.messageText = '';
    this.imageSrc = null;
  }
}
