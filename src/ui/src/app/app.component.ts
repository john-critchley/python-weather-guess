import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  public title: string = 'img-uploader';
  public word?: string;

  public handleWord(word: string): void {
    console.log(word);
    this.word = word;
  }
}
