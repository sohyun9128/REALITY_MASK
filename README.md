# REALITY_MASK

### 출처 : https://github.com/tensorflow/tpu  
!git clone https://github.com/tensorflow/tpu  
  
## 0. 개요  
본 프로그램는 기존에 존재하는 기술과 달리 실감이 극대화되는 실감형 서비스를 제공하기위해 2D영상을 3D 그래픽으로 구현하고, 각 객체들의 시점 영상을 제공하는 것을 목표로 한다. 단순히 객체의 3D모델만을 구현하는 것이 아니라 다양한 객체들의 이동과 그에 따른 3인칭, 1인칭 시점을 자유선택 시점으로서 제공할 수 있다는 것이 본 프로그램의 핵심이다. 이는 사용자에게 자유로운 방향, 시점, 위치, 인칭을 선택하여 원하는 영상을 제공한다. 본 파일은 REALITY 중 객체를 탐지하고 구분하는 부분에 대한 코드만을 포함한다.  

## 1. Function
### 1) toImages()
동영상을 이미지로 변환해주는 함수.  
Args:  
- img_path: 변환할 이미지를 저장할 경로.  
- input_video_file: 이미지로 변환할 비디오 경로.  

Output:  
- imgs_path 폴더에 캡쳐된 이미지들 저장.  
  
  
### 2) maskRcnn()  
이미지 속 객체를 탐지하고 객체들의 class와 위치 좌표를 저장하는 함수.    
Args:  
- imgs_path: 객체를 탐지할 이미지들이 포함되어있는 이미지 폴더.  

Output:  
- output_path 폴더에 txt형태로 객체 정보들을 저장.  

  
### 3) objectIndexing()  
같은 Class에 속하는 객체들을 구분하여 id값을 지정해주는 함수  
Args:  
- beforeF, afterF : 연이은 프레임의 객체 인식 정보
- max_id : id의 최대값

Output:  
- [해당 프레임 객체들의 id 값이 담긴 list, 업데이트 된 max_id]  
  
---
  
## 2. Output 형식  
1) maskRcnn output file  
객체 Class (tab) 객체 중심의 x좌표 (tab) 객체 중심의 y좌표  
![image](https://user-images.githubusercontent.com/50349511/131222204-fac94a82-be8b-4e74-a4dc-a9f2f8c741e2.png)
  
2) objectIndexing output file   
  "frame" (tab) 프레임 번호 (tab) 해당 프레임이 존재하는 객체의 수  
  객체id (tab) 객체 중심의 x좌표 (tab) 객체 중심의 y좌표  
![image](https://user-images.githubusercontent.com/50349511/131222294-a382dd86-e468-4e07-8653-82bb0c2f1012.png)  
참고 : 현재 버전에서는 Person class 객체만 다루기 때문에 class 열은 삭제  

