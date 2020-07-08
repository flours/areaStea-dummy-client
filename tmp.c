#include<stdio.h>

void run(){
    int *a;
    a=(int*)malloc(sizeof(int));
    *a=1;
    printf("%d",*a);
    free(a);
}

int main(void){
    // Your code here!
    run();

}

