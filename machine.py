import random
from itertools import combinations
from shapely.geometry import LineString, Point

from itertools import product, chain, combinations
from shapely.geometry import LineString, Point, Polygon
import math

class MACHINE():
    """
        [ MACHINE ]
        MinMax Algorithm을 통해 수를 선택하는 객체.
        - 모든 Machine Turn마다 변수들이 업데이트 됨

        ** To Do **
        MinMax Algorithm을 이용하여 최적의 수를 찾는 알고리즘 생성
           - class 내에 함수를 추가할 수 있음
           - 최종 결과는 find_best_selection을 통해 Line 형태로 도출
               * Line: [(x1, y1), (x2, y2)] -> MACHINE class에서는 x값이 작은 점이 항상 왼쪽에 위치할 필요는 없음 (System이 organize 함)
    """
    def __init__(self, score=[0, 0], drawn_lines=[], whole_lines=[], whole_points=[], location=[]):
        self.id = "MACHINE"
        self.score = [0, 0] # USER, MACHINE
        self.drawn_lines = [] # Drawn Lines
        self.board_size = 7 # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = []
        self.location = []
        self.triangles = [] # [(a, b), (c, d), (e, f)]


# best selection 고치면될듯
    def find_best_selection(self):
        # 가능한 선분들

        available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]
        print(available)
        max_distance = 0 # 가장 멀리 그을 수 있는거 (단독/연결 고려 X)
        max_index = 0  # 이때의 index
        max_disconnected_index = -1  # 아무것도 연결 안되어있는것중에 긴 선분의 index
        index_distance_dict = {}


        # 0. 사각형 반가르는거면 ㄱㄱㄱㄱ0순위
        for i in range(len(available)):
            line = available[i]
            if(self.check_rectangle(line)):
                # 무조건 ㄱㄱ
                return line

        # 1. 삼각형 만들 수 있으면 바로 ㄱ  
        for i in range(len(available)):
            line = available[i]

            if(self.check_triangle(line)):
                return line
            

        # 2. 가장 길게 그을 수 있는거
            distance = math.sqrt((line[0][0]-line[1][0])**2 + (line[0][1]-line[1][1])**2)
            if(max_distance<distance):
                max_distance = distance
                max_index = i

            # index_distance 정보 저장
            index_distance_dict[i] = distance
        
        # distance기준으로 내림차순 정렬
        index_distance_dict = dict(sorted(index_distance_dict.items(), key=lambda item: item[1], reverse=True))

        # 길게 그을 수 있는 순으로 상대에게 기회 주지 않는 선 찾기
        # 3. 한 수 앞 예측
        for idd in index_distance_dict:
            if(self.see_next_turn(available[idd], available)):
                return available[idd]

        # 4. 만들 수 있는 삼각형 없으면 제일 먼줄로 긋기
        return available[max_index]
    
    
    def see_next_turn(self, line, available):
        point1 = line[0]
        point2 = line[1]
        for l in self.drawn_lines:
            if(point1 in l):
                idx = abs(l.index(point1)-1)  # idx를 0or1로 바꾸고 
                point0 = l[idx]
                for al in available:
                    if(point0 in al and point2 in al): # 상대가 삼각형 만들 수 있음(하나라도 존재하면 안됨)

                        # 안에 점 존재 -> continue(그어도됨)
                        # 안에 점 없음 -> False(안됨)
                        return False
            if(point2 in l):
                idx = abs(l.index(point2)-1)  # idx를 0or1로 바꾸고 
                point0 = l[idx]
                for al in available:
                    if(point0 in al and point1 in al): # 상대가 삼각형 만들 수 있음
                        
                        # 안에 점 존재 -> continue(그어도됨)
                        # 안에 점 없음 -> False(안됨)
                        return False
        print("다음수에 상대가 할 거 없음!")           
        return True  # t상대가 만들 수 있는 삼각형이 없음 -> 그어도됨
        
    # 사각형 찾기
    def check_rectangle(self, line):
        point1 = line[0]
        point2 = line[1]

        point1_connected = []
        point2_connected = []

        for l in self.drawn_lines:
            if(point1 in l):
                point1_connected.append(l)
            if point2 in l:
                point2_connected.append(l)
        if(len(point1_connected)>=2 and len(point2_connected)>=2):
            for line1, line2 in product(point1_connected, point2_connected):
                if((line1[0] in line2 or line1[1] in line2) and (line2[0] in line1 or line2[1] in line1)):
                    if(line1[0] in line2):
                        point0 = line1[0]
                    else:
                        point0 = line1[1]
                    if(line2[0] in line2):
                        point00 = line2[0]
                    else:
                        point00 = line2[1]

                    if((self.check_pointIntri(point1, point2, point0)) and (self.check_pointIntri(point1, point2, point00))):
                        return True
        return False




    # 삼각형 찾기
    def check_triangle(self, line):
        point1 = line[0]
        point2 = line[1]

        point1_connected = []
        point2_connected = []

        for l in self.drawn_lines:
            if point1 in l:
                point1_connected.append(l)
            if point2 in l:
                point2_connected.append(l)

        if point1_connected and point2_connected: # 최소한 2점 모두 다른 선분과 연결되어 있어야 함
            # product는 모든 조합 구해줌
            for line1, line2 in product(point1_connected, point2_connected):
                #print("line1 line2: ", line1, line2)
                if(line1[0] in line2):                 
                    if(self.check_pointIntri(point1, point2, line1[0])):
                        return True
                if(line1[1] in line2):
                    print("3개의 선: ", line, line1, line2)
                    if(self.check_pointIntri(point1, point2, line1[1])):
                        return True
        return False
        # 한수앞을 보자


    #삼각형 내부의 점 체크
    def check_pointIntri(self, tripoint1, tripoint2, tripoint3):
        triangle = Polygon([tripoint1, tripoint2, tripoint3])
        for point in self.whole_points:
            p = Point(point)
            if(p == tripoint1 or p == tripoint2 or p == tripoint3):
                continue
            else:
                if p.within(triangle):
                    return False
        return True
    
    def check_availability(self, line):
        line_string = LineString(line)

        # Must be one of the whole points
        condition1 = (line[0] in self.whole_points) and (line[1] in self.whole_points)
        
        # Must not skip a dot
        condition2 = True
        for point in self.whole_points:
            if point==line[0] or point==line[1]:
                continue
            else:
                if bool(line_string.intersection(Point(point))):
                    condition2 = False

        # Must not cross another line
        condition3 = True
        for l in self.drawn_lines:
            if len(list(set([line[0], line[1], l[0], l[1]]))) == 3:
                continue
            elif bool(line_string.intersection(LineString(l))):
                condition3 = False

        # Must be a new line
        condition4 = (line not in self.drawn_lines)

        if condition1 and condition2 and condition3 and condition4:
            return True
        else:
            return False    

        