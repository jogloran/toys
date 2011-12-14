data Colour = R | B
data RBNode a = Empty | Node Colour (RBNode a) a (RBNode a)

instance Show Colour where
    show R = "R"
    show B = "B"
    
-- instance Show a => Show (RBNode a) where
--     show Empty = "_"
--     show (Node c l x r) = "(" ++ (show c) ++ " " ++ (show l) ++ " " ++ (show x) ++ " " ++ (show r) ++ ")"

instance Show a => Show (RBNode a) where
    show Empty = ""
    show (Node c l x r) = "(" ++ (show l) ++ " " ++ (show x) ++ " " ++ (show r) ++ ")"

find v Empty = False
find v (Node _ l x r) | v < x     = find v l
                      | v > x     = find v r
                      | otherwise = True
                      
insert v n = Node B l x r where
    (Node _ l x r) = ins v n
    ins v n@(Node c l x r) | v < x = balance $ Node c (ins v l) x r
                           | v > x = balance $ Node c l x (ins v r)
                           | otherwise = n
    ins v Empty = Node R Empty v Empty
                          
balance (Node _ alpha v1 (Node R beta v2 (Node R gamma v3 delta))) =
    (Node R (Node B alpha v1 beta) v2 (Node B gamma v3 delta))
balance (Node _ (Node R (Node R alpha v3 beta) v2 gamma) v1 delta) =
    (Node R (Node B alpha v1 beta) v2 (Node B gamma v3 delta))
balance (Node _ (Node R alpha v2 (Node R beta v3 gamma)) v1 delta) =
    (Node R (Node B alpha v1 beta) v2 (Node B gamma v3 delta))
balance (Node _ alpha v1 (Node R (Node R beta v3 gamma) v2 delta)) =
    (Node R (Node B alpha v1 beta) v2 (Node B gamma v3 delta))
balance t = t
    
main = do
    return $ insert 3 Empty