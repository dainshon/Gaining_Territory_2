import random
import math
from itertools import product, chain, combinations
from shapely.geometry import LineString, Point, Polygon

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
        self.num_turns = 0
        self.limit = 0
        self.num_turns = 0
        self.drawn_lines_with_turns = [] # 선과 그어진 턴도 같이 저장

        self.available_line_triangle = []
        
    
    def draw_line(self, line_coords, turn):
        self.drawn_lines.append(line_coords)
        self.drawn_lines_with_turns.append((line_coords, turn))

    def increment_turn(self):
        self.num_turns += 1 

    def set_num_from_dots(self):
        self.num_dots = len(self.whole_points)

        if self.num_dots <= 15:
            self.limit = 10
        else:
            self.limit = 15
    
    def valid_move(self):
        return [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]

    
    def update_triangles(self, drawn_line, current_turn):
        # 선이 그어지면 삼각형 업데이트
        triangles_completed = []
        for triangle in self.triangles:
            triangle_completed = True
            for line in combinations(triangle, 2):
                if (line, current_turn) not in self.drawn_lines_with_turns:
                    triangle_completed = False
                    break

            if triangle_completed:
                triangles_completed.append(triangle)

        # 만들어진 턴과 함께 삼각형 저장
        for triangle in triangles_completed:
            self.triangles.remove(triangle)
            self.triangles.append((triangle[0], triangle[1], drawn_line, current_turn))

    def undo_move(self, line, current_turn):
        if line in self.drawn_lines:  # line이 있는지 일단 확인(충돌 방지)
            self.drawn_lines.remove(line)

            # 시뮬레이션 끝나고 선 그은거 undo
            for i, entry in enumerate(self.drawn_lines_with_turns):
                if entry[0] == line and entry[1] == current_turn:
                    del self.drawn_lines_with_turns[i]
                    break 
       

    def undo_triangle(self, line, current_turn):
        if line in self.drawn_lines:  # line이 있는지 일단 확인
            self.drawn_lines.remove(line)
            # 시뮬레이션 끝나고 undo
            triangles_to_undo = []
            for triangle in self.triangles:
                if triangle[2] == line and triangle[3] == current_turn:
                    triangles_to_undo.append(triangle)
            for triangle in triangles_to_undo:
                self.triangles.remove(triangle)
                self.triangles.append((triangle[0], triangle[1]))
        
    
    def count_triangles_now(self, turn):
        triangles_count = 0
        for triangle in self.triangles:
            triangle_completed = True
            for line in combinations(triangle, 2):
                if (line, turn) not in self.drawn_lines_with_turns:
                    triangle_completed = False
                    break
            
            if triangle_completed:
                triangles_count += 1
        
        return triangles_count
    
    def heuristic_function(self):
        machine_triangles = self.count_triangles_now("MACHINE")
        user_triangles = self.count_triangles_now("USER")

        return machine_triangles, user_triangles
    

    
    def min_max(self, depth, alpha, beta, maximizing_player, current_turn):
        
        if depth == 0 or not self.valid_move():
            machine_heuristic, user_heuristic = self.heuristic_function()

            if maximizing_player:  # Maximizer's turn (MACHINE)
                return machine_heuristic
            else:  # Minimizer's turn (USER)
                return user_heuristic

        if maximizing_player:  # Maximizer's turn (MACHINE)
            best_value = -math.inf
            for move in self.valid_move():
                self.draw_line(move, current_turn)  # Make a move
                self.update_triangles(move, current_turn)
                value = self.min_max(depth - 1, alpha, beta, False, 'USER')  # Switch to opponent's turn
                self.undo_move(move, current_turn) 
                self.undo_triangle(move, current_turn)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            return best_value
        else:  # Minimizer's turn (USER)
            best_value = math.inf
            for move in self.valid_move():
                self.draw_line(move, current_turn)
                self.update_triangles(move, current_turn)
                value = self.min_max(depth - 1, alpha, beta, True, 'MACHINE')
                self.undo_move(move, current_turn) 
                self.undo_triangle(move, current_turn)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            return best_value

    
    def find_best_selection(self): # depth 3 = 50초(1턴) 25초 (2턴) 14초(3턴), depth 4 = 9분쯤
        print("----------------------------")
        self.increment_turn()
        self.set_num_from_dots()
        available = self.valid_move()
        num_available_line = len(available)
        print("available 길이: ", num_available_line)

        available_line_triangle = []  # 삼각형 만들 수 있는 선 모음 

        max_distance = 0 # 가장 멀리 그을 수 있는거 (단독/연결 고려 X)
        max_index = 0  # 이때의 index
        max_disconnected_index = -1  # 아무것도 연결 안되어있는것중에 긴 선분의 index
        index_distance_dict = {}


        if(num_available_line > 4):
            # 0. 사각형 반가르는거면 ㄱㄱㄱㄱ0순위
            for i in range(len(available)):
                line = available[i]
                if(self.check_rectangle(line)):
                    # 무조건 ㄱㄱ
                    return line
            
            # 1. 삼각형 만들 수 있으면 ㄱ  
            for i in range(len(available)):
                line = available[i]
                flag = 1
                if(self.check_triangle(line)):
                    print("추가!")
                    available_line_triangle.append(line)

                # 2. 가장 길게 그을 수 있는거
                distance = math.sqrt((line[0][0]-line[1][0])**2 + (line[0][1]-line[1][1])**2)
                if(max_distance<distance):
                    max_distance = distance
                    max_index = i

                # index_distance 정보 저장
                index_distance_dict[i] = distance

            print("가능한 삼각형: ", available_line_triangle)
            total = len(available_line_triangle)*num_available_line

            if(total > 150 or (len(available_line_triangle)>3 and total >100)):
                print("너무 커서 안됨")
                return available_line_triangle[0]
            
            if(len(available_line_triangle)==1):
                return available_line_triangle[0]
            
            if(len(available_line_triangle)!=0):  # 삼각형 만들 수 있으면
                print("삼각형은 있지만: ", available_line_triangle)
                best_value = -math.inf
                best_selection = None
                alpha = -math.inf
                beta = math.inf
                best_score = -math.inf 

                for move in available_line_triangle:
                    self.drawn_lines.append(move)
                    self.update_triangles(move, 'MACHINE')
                    value = self.min_max(3, alpha, beta, True ,'MACHINE') # False: opponent's turn
                    self.drawn_lines.remove(move)
                    self.undo_triangle(move, 'MACHINE')
                    if value > best_value: # best move 정하기
                        best_value = value
                        best_selection = move
                        alpha = max(alpha,best_value)
                return best_selection
                        
                # distance기준으로 내림차순 정렬
            index_distance_dict = dict(sorted(index_distance_dict.items(), key=lambda item: item[1], reverse=True))
        

        # 삼/사각형 만들 수 없다면 그때부터  rule/minmax 고민
        if(num_available_line>self.limit):
            # 길게 그을 수 있는 순으로 상대에게 기회 주지 않는 선 찾기
            # 3. 한 수 앞 예측
            for idd in index_distance_dict:
                if(self.see_next_turn(available[idd], available)):
                    return available[idd]

                # 4. 만들 수 있는 삼각형 없으면 제일 먼줄로 긋기
            return available[max_index]

        else:
            print("minmax")
            best_value = -math.inf
            best_selection = None
            alpha = -math.inf
            beta = math.inf
            best_score = -math.inf 

            for move in self.valid_move():
                self.drawn_lines.append(move)
                self.update_triangles(move, 'MACHINE')
                value = self.min_max(3, alpha, beta, True ,'MACHINE') # False: opponent's turn
                self.drawn_lines.remove(move)
                self.undo_triangle(move, 'MACHINE')
                if value > best_value: # best move 정하기
                    best_value = value
                    best_selection = move
                    alpha = max(alpha,best_value)
            

            return best_selection
        
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
        
        
    def see_next_turn(self, line, available):
        point1 = line[0]
        point2 = line[1]
        for l in self.drawn_lines:
            if(point1 in l):
                idx = abs(l.index(point1)-1)  # idx를 0or1로 바꾸고 
                point0 = l[idx]
                for al in available:
                    if(point0 in al and point2 in al): # 상대가 삼각형 만들 수 있음(하나라도 존재하면 안됨)
                        if(self.check_pointIntri(point0, point1,point2)): # (상대가 그을 삼각형에)점 없음
                            return False
                        else:
                            continue
                        
            if(point2 in l):
                idx = abs(l.index(point2)-1)  # idx를 0or1로 바꾸고 
                point0 = l[idx]
                for al in available:
                    if(point0 in al and point1 in al): # 상대가 삼각형 만들 수 있음
                        if(self.check_pointIntri(point0, point1,point2)): # (상대가 그을 삼각형에)점 없음
                            return False
                        else:
                            continue

                        return False
        print("다음수에 상대가 할 거 없음!")           
        return True  # t상대가 만들 수 있는 삼각형이 없음 -> 그어도됨
        
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
        cnt = 0
        if(len(point1_connected)>=2 and len(point2_connected)>=2):
            for line1, line2 in product(point1_connected, point2_connected):
                if((line1[0] in line2 or line1[1] in line2) ):
                    if(line1[0] in line2):
                        point0 = line1[0]
                    else:
                        point0 = line1[1]
                    if(line2[0] in line2):
                        point00 = line2[0]
                    else:
                        point00 = line2[1]

                    if((self.check_pointIntri(point1, point2, point0)) and (self.check_pointIntri(point1, point2, point00))):
                        print("check_rectangle")
                        cnt+=1
            if(cnt>=2):
                return True
                        #return True
                #if(and (line2[0] in line1 or line2[1] in line1))
        return False

    
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
                    #print("3개의 선: ", line, line1, line2)
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
                    return False  # 안에 점 있음
        return True  # 안에 점 없음
    