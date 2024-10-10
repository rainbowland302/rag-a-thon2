import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from "@angular/forms";

import { ClarityModule } from "@clr/angular";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ClarityModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  search = ""
}
