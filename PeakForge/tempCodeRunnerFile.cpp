#include <iostream>
#include <vector>
using namespace std;
int main(){
vector <int>a={1,3,5,5,7,3,3,2,1,1,2,6,8};
sort(a.begin(),a.end());
for(int i=0;i<a.size();i++){
    cout<<a[i]<<" ";
}
cout<<a.back()<<" ";}
