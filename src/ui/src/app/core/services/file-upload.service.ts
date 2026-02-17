import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { interval, Observable } from 'rxjs';
// import {  of } from 'rxjs';
import { takeWhile, tap } from 'rxjs/operators';
import { flatMap } from 'rxjs/internal/operators';

const IN_PROGRESS = 'Recognition in progress';

@Injectable({
  providedIn: 'root',
})
export class FileUploadService {
  private isRecognitionInProgress: boolean = false;
  // private counter: number = 0;

  constructor(
    private readonly http: HttpClient,
  ) {
  }

  public uploadFile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<any>('http://localhost:8080/categorize', formData);
    // return of('123');
  }

  public pollFileDataById(id: string): Observable<any> {
    this.isRecognitionInProgress = true;
    return interval(1000)
      .pipe(
        flatMap(() => this.getFileDataById(id)),
        takeWhile(() => this.isRecognitionInProgress),
        tap((data) => {
            console.log(data.text);
            return this.isRecognitionInProgress = data.text === IN_PROGRESS;
        }),
      )
  }

  public getFileDataById(id: string): Observable<any> {
    return this.http.get<any>(`http://localhost:8080/categorize/${ id }`);
    // this.counter++;
    // return this.counter < 3  ? of(IN_PROGRESS) : of('cat');
  }

}
