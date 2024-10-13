import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from "@angular/forms";
import { ClarityModule } from "@clr/angular";
import { CommonModule } from '@angular/common';

import { AppService } from "./app.service";

interface QueryResponse {
  question: string;
  answer: string;
  timestamp: Date;
  imageUrl?: string;
  audioUrl?: string;
}

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [RouterOutlet, ClarityModule, FormsModule, CommonModule],
    providers: [AppService],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent {
    constructor(
        private service: AppService,
    ) {}

    message = "";
    responses: QueryResponse[] = [];
    isLoading = false;
    currentBackgroundImage: string | null = null;
    nextBackgroundImage: string | null = null;
    isTransitioning = false;
    currentAudio: HTMLAudioElement | null = null;

    search() {
        if (!this.message.trim()) return;
        
        this.isLoading = true;
        const question = this.message;
        this.isTransitioning = true;
        this.service.retrieveAns(this.message).subscribe({
            next: (res: any) => {
                this.responses.unshift({
                    question: question,
                    answer: res.res,
                    timestamp: new Date(),
                    imageUrl: res.img,
                    audioUrl: res.aud
                });
                this.preloadAndUpdateBackgroundImage(res.img);
                this.isLoading = false;
            },
            error: (err) => {
                console.error('Error:', err);
                this.isLoading = false;
            }
        });
        this.message = "";
    }

    preloadAndUpdateBackgroundImage(newImageUrl: string) {
        if (this.nextBackgroundImage !== newImageUrl) {
            const img = new Image();
            console.log("preloading");
            img.onload = () => {
                console.log("loaded");
                this.isTransitioning = true;
                this.nextBackgroundImage = newImageUrl;
                setTimeout(() => {
                    console.log("transitioning done");
                    this.isTransitioning = false;
                    setTimeout(() => {
                        console.log("change current to next");
                        this.currentBackgroundImage = this.nextBackgroundImage;
                    }, 2000); // Match this with the faster fade-in duration
                }, 500); // Match this with the slower fade-out duration
            };
            img.src = newImageUrl;
        }
    }

    playAudio(response: QueryResponse) {
        if (response.audioUrl) {
            if (this.currentAudio) {
                this.currentAudio.pause();
                this.currentAudio = null;
            }
            this.currentAudio = new Audio(response.audioUrl);
            this.currentAudio.play();
        }
    }

    stopAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
    }
}
