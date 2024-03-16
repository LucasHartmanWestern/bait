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
  feedbackRating: number = 0
  callEnded: boolean = false;

  messages: any[] = [
    { role: 'user', content: [{ type: 'text', text: 'I am doing a project for school, can you act as a representative for Bell customer support when I send you questions and images pertaining to Bell. After each response, also provide 2 suggested follow-up messages the USER can send (NOT THE SYSTEM). The format your messages ALL need to follow is as such: "Response goes here" <div><span>"Follow up 1 goes here"</span><span>"Follow up 2 goes here"</span></div> Here is an example: Hello, I\'m sorry to hear your router is not working. Can you send me some details about your router so I can better assist you?<div><span>I don\'t know what my router is?</span><span>How do I find that info?</span></div>'}]},
    { role: 'system', content: [{type: 'text', text: 'Hello, I am Bell Customer support. How can I help you today?<div><span>I need help with my wifi.</span><span>Tell me about the new promos.</span></div>'}]}
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

  speakAI(text: string): void {
    let final = '';
    let output = text.split('<div><span>')
    if (output.length > 1) {
      let options = output[1].split('</span><span>')
      options[1] = options[1].replace('</span></div>', '')

      final = `${output[0]} Suggested option 1: ${options[0]} Suggested option 2: ${options[1]}`;
    } else {
      final = output[0];
    }

    const speech = new SpeechSynthesisUtterance(final);
    window.speechSynthesis.speak(speech);
  }

  endSession(): void {
    this.callEnded = true;
    let feedbackMessage = {
      role: 'system',
      content: [{type: 'text', text: `
        <div>Please leave a rating on your experience today</div>
        <div class="star-rating">
          <span title="1">&#9733;</span>
          <span title="2">&#9733;</span>
          <span title="3">&#9733;</span>
          <span title="4">&#9733;</span>
          <span title="5">&#9733;</span>
        </div>
        <div>
            <span class="submit-btn">Submit</span>
        </div>`}]
    }

    this.messages.push(feedbackMessage);
    this.removeQuickResponses();
    setTimeout(() => {
      document.querySelector('.submit-btn')?.addEventListener('click', (event) => {
        this.submitFeedback(this.feedbackRating);
      });

      document.querySelector('.star-rating')?.addEventListener('click', (event) => {
        if((event.target as HTMLElement).tagName === 'SPAN') {
          let rating = Number((event.target as HTMLElement).getAttribute('title'));
          this.feedbackRating = rating;
          let stars = (event.target as HTMLElement).parentNode?.querySelectorAll('span');
          stars?.forEach((star: HTMLElement) => {
            let starVal = Number(star.getAttribute('title'));
            if(starVal <= rating) {
              star.classList.add('selected');
            } else {
              star.classList.remove('selected');
            }
          });
        }
      });
    }, 500);
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
      this.updateQuickResponseEvents();
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
      this.messages.push({role: 'user', content: [{type: 'text', text: message}]})
    if (this.imageSrc)
      this.messages.push({role: 'user', content: [{type: 'image_url', image_url: {url: this.imageSrc}}], sendAPI: false})

    this.loading = true;

    this.messageService.sendMessage(this.messages, this.imageSrc).subscribe(res => {
      this.loading = false;
      this.messages.push({role: 'system', content: [{type: 'text', text: res?.response}], pdf: res?.pdf});
      setTimeout(() => {
        this.updateQuickResponseEvents();
      }, 500);
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

  submitFeedback(rating: number): void {
    let btn = document.querySelector('.submit-btn') as HTMLElement;
    btn?.parentNode?.removeChild(btn || document.createElement('button'));
    let stars = document.querySelector('.message_bubble.system > .star-rating');
    let new_stars = stars?.cloneNode(true);
    if (new_stars)
      stars?.parentNode?.replaceChild(new_stars, stars);

    this.messageService.sendFeedback(this.messages, rating).subscribe(res => {
      console.log("Feedback Submitted");
    }, error => console.log(error));

    if (rating < 3)
      this.askJIRA();
  }

  askJIRA(): void {
    let feedbackMessage = {
      role: 'system',
      content: [{type: 'text', text:`
        <div>Sorry you had a below-average experience. Would you like to submit a support ticket?</div>
        <div class="jiraText"></div>
        <div>
            <span class="submit-jira">Submit</span>
        </div>`}]
    }

    this.messages.push(feedbackMessage);

    setTimeout(() => {
      let jiraTextEl = document.querySelector('.jiraText') as HTMLElement;
      let textInput = document.createElement('textarea');
      textInput.placeholder = 'Submit Concern Here...';
      jiraTextEl.appendChild(textInput);
      document.querySelector('.submit-jira')?.addEventListener('click', (event) => {
        let textBox = (event.target as HTMLElement)?.parentNode?.parentNode?.querySelector('textarea');
        let feedback = textBox?.value;
        (event.target as HTMLElement)?.parentNode?.parentNode?.removeChild(document.querySelector('.jiraText') || document.createElement('button'));
        (event.target as HTMLElement)?.parentNode?.removeChild((event.target as HTMLElement));
        this.messages.push({role: 'user', content: [{type: 'text', text: feedback || ''}]})
        this.submitJiraTicket(feedback);
      });
    }, 100);
  }

  submitJiraTicket(message: string | undefined): void {
    let feedbackMessage = {
      role: 'system',
      content: [{type: 'text', text: 'Thank you, your ticket has been created'}]
    }

    this.messages.push(feedbackMessage);

    this.messageService.sendJIRA(message || '').subscribe(res => {
      console.log("Feedback Submitted");
    }, error => console.log(error))
  }

  removeQuickResponses(): void {
    let spans = document.querySelectorAll('.message_bubble.system > .message_content > div > span');
    spans.forEach(span => {
      if (span.innerHTML != '&#9733')
        span?.parentNode?.removeChild(span);
    });
  }

  updateQuickResponseEvents(): void {
    let quickResponses = document.querySelectorAll('.message_bubble.system > .message_content > div > span');
    console.log(quickResponses);
    quickResponses.forEach(span => {
      let new_span = span.cloneNode(true);
      new_span.addEventListener("click", (event) => {
        this.sendMessage((event.target as HTMLElement).textContent || '');
        (event?.target as HTMLElement)?.parentNode?.parentNode?.removeChild((event?.target as HTMLElement)?.parentNode || document.createElement('button'));
      });
      span?.parentNode?.replaceChild(new_span, span);
    });

    let chatDiv = document.querySelector('.chat');
    if (chatDiv) {
      chatDiv.scrollTo({
        top: chatDiv.scrollHeight,
        behavior: 'smooth'
      });
    }
  }
}
