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

  messages: {role: string, content: string, sendAPI?: boolean}[] = [
    { role: 'user', content: 'I am doing a project for school, can you act as a representative for Bell customer support when I send you questions and images pertaining to Bell.' },
    { role: 'system', content: 'Hello, I am Bell Customer support. How can I help you today?' }
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

    document?.querySelector('.message_input')?.addEventListener('input', (event) => {
      const target = event.target as HTMLTextAreaElement;
      target.style.height = 'auto';
      if (target.scrollHeight > 100) {
        target.style.overflowY = 'auto';
        target.style.height = '100px';
      } else {
        target.style.overflowY = 'hidden';
        target.style.height = target.scrollHeight + 'px';
      }
      target.scrollTop = target.scrollHeight;
    });

    document.addEventListener('paste', (event) => {
      let clipboardData = event.clipboardData;
      let items = clipboardData?.items;
      if (items) {
        for (let i = 0; i < items.length; i++) {
          if (items[i].type.indexOf('image') === 0) {
            let file = items[i].getAsFile();
            if (file) { // Check that the file is not null
              let blob = file as Blob; // Type assertion: File is a Blob
              let reader = new FileReader();

              reader.onload = (event) => {
                let base64String = event?.target?.result;
                if (base64String) {
                  this.imageSrc = base64String;
                }
              };

              reader.readAsDataURL(blob);
            }
          }
        }
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
    if (message)
      this.messages.push({role: 'user', content: message})
    if (this.imageSrc)
      this.messages.push({role: 'user', content: `<img src='${this.imageSrc}' />`, sendAPI: false})

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

    const target = document?.querySelector('.message_input') as HTMLTextAreaElement;
    target.style.height = 'auto';
    target.style.overflowY = 'hidden';
  }
}
