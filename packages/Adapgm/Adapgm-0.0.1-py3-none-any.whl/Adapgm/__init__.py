def p1():
    return """#include <stdio.h>

// Function to merge two subarrays of arr[]
// First subarray is arr[l..m]
// Second subarray is arr[m+1..r]
void merge(int arr[], int l, int m, int r) {
    int i, j, k;
    int n1 = m - l + 1;
    int n2 = r - m;

    // Create temporary arrays
    int L[n1], R[n2];

    // Copy data to temporary arrays L[] and R[]
    for (i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[m + 1 + j];

    // Merge the temporary arrays back into arr[l..r]
    i = 0; // Initial index of first subarray
    j = 0; // Initial index of second subarray
    k = l; // Initial index of merged subarray
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    // Copy the remaining elements of L[], if there are any
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }

    // Copy the remaining elements of R[], if there are any
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

// Main function to perform merge sort on arr[l..r]
void mergeSort(int arr[], int l, int r) {
    if (l < r) {
        // Find the middle point
        int m = l + (r - l) / 2;

        // Sort first and second halves
        mergeSort(arr, l, m);
        mergeSort(arr, m + 1, r);

        // Merge the sorted halves
        merge(arr, l, m, r);
    }
}

// Function to print an array
void printArray(int arr[], int size) {
    for (int i = 0; i < size; i++)
        printf("%d ", arr[i]);
    printf("\n");
}

int main() {
    int arr[] = {12, 11, 13, 5, 6, 7};
    int arr_size = sizeof(arr) / sizeof(arr[0]);

    printf("Given array is \n");
    printArray(arr, arr_size);

    mergeSort(arr, 0, arr_size - 1);

    printf("Sorted array is \n");
    printArray(arr, arr_size);
    return 0;
}
"""

def p2():
    return """#include <stdio.h>

// Function to swap two elements
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// Function to partition the array and return the pivot index
int partition(int arr[], int low, int high) {
    int pivot = arr[high]; // Choose the rightmost element as the pivot
    int i = (low - 1); // Initialize the index of the smaller element

    for (int j = low; j <= high - 1; j++) {
        // If the current element is smaller than or equal to the pivot
        if (arr[j] <= pivot) {
            i++; // Increment index of the smaller element
            swap(&arr[i], &arr[j]);
        }
    }

    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

// Function to perform Quick Sort
void quickSort(int arr[], int low, int high) {
    if (low < high) {
        // Find pivot such that element smaller than pivot are on the left,
        // and elements greater than pivot are on the right
        int pi = partition(arr, low, high);

        // Recursively sort elements before and after pivot
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

// Function to print an array
void printArray(int arr[], int size) {
    for (int i = 0; i < size; i++)
        printf("%d ", arr[i]);
    printf("\n");
}

int main() {
    int arr[] = {12, 11, 13, 5, 6, 7};
    int arr_size = sizeof(arr) / sizeof(arr[0]);

    printf("Given array is \n");
    printArray(arr, arr_size);

    quickSort(arr, 0, arr_size - 1);

    printf("Sorted array is \n");
    printArray(arr, arr_size);
    return 0;
}
"""

def p3():
    return """#include <stdio.h>

// Function to find the maximum and minimum elements in an array
void findMaxMin(int arr[], int n, int* max, int* min) {
    if (n == 0) {
        printf("Array is empty.\n");
        return;
    }

    *max = arr[0]; // Initialize max and min with the first element
    *min = arr[0];

    for (int i = 1; i < n; i++) {
        if (arr[i] > *max) {
            *max = arr[i]; // Update max if a larger element is found
        }
        if (arr[i] < *min) {
            *min = arr[i]; // Update min if a smaller element is found
        }
    }
}

int main() {
    int arr[] = {12, 11, 13, 5, 6, 7};
    int n = sizeof(arr) / sizeof(arr[0]);
    int max, min;

    findMaxMin(arr, n, &max, &min);

    printf("Maximum element in the array: %d\n", max);
    printf("Minimum element in the array: %d\n", min);

    return 0;
}
"""

def p4():
    return """#include <stdio.h>
#include <stdlib.h>

#define MAX_VERTICES 100

// Structure to represent a vertex in the graph
struct Vertex {
    int data;
    struct Vertex* next;
};

// Structure to represent a directed acyclic graph (DAG)
struct DAG {
    int numVertices;
    struct Vertex* adjacencyList[MAX_VERTICES];
    int* inDegree; // Array to store in-degrees of vertices
};

// Function to create a new vertex
struct Vertex* createVertex(int data) {
    struct Vertex* newVertex = (struct Vertex*)malloc(sizeof(struct Vertex));
    newVertex->data = data;
    newVertex->next = NULL;
    return newVertex;
}

// Function to create a new DAG with 'n' vertices
struct DAG* createDAG(int n) {
    struct DAG* graph = (struct DAG*)malloc(sizeof(struct DAG));
    graph->numVertices = n;
    for (int i = 0; i < n; i++) {
        graph->adjacencyList[i] = NULL;
    }
    graph->inDegree = (int*)calloc(n, sizeof(int));
    return graph;
}

// Function to add a directed edge from vertex 'from' to vertex 'to'
void addEdge(struct DAG* graph, int from, int to) {
    struct Vertex* newVertex = createVertex(to);
    newVertex->next = graph->adjacencyList[from];
    graph->adjacencyList[from] = newVertex;
    graph->inDegree[to]++;
}

// Function to perform topological sorting using DFS
void topologicalSortDFS(struct DAG* graph, int vertex, int visited[], int* stack, int* stackIndex) {
    visited[vertex] = 1;

    struct Vertex* adjVertex = graph->adjacencyList[vertex];
    while (adjVertex != NULL) {
        int adjData = adjVertex->data;
        if (!visited[adjData]) {
            topologicalSortDFS(graph, adjData, visited, stack, stackIndex);
        }
        adjVertex = adjVertex->next;
    }

    stack[(*stackIndex)] = vertex;
    (*stackIndex)++;
}

// Function to perform topological sorting of the DAG
void topologicalSort(struct DAG* graph) {
    int* visited = (int*)calloc(graph->numVertices, sizeof(int));
    int* stack = (int*)malloc(graph->numVertices * sizeof(int));
    int stackIndex = 0;

    for (int i = 0; i < graph->numVertices; i++) {
        if (!visited[i]) {
            topologicalSortDFS(graph, i, visited, stack, &stackIndex);
        }
    }

    printf("Topological Order: ");
    for (int i = graph->numVertices - 1; i >= 0; i--) {
        printf("%d ", stack[i]);
    }
    printf("\n");

    free(visited);
    free(stack);
}

int main() {
    struct DAG* graph = createDAG(6);

    addEdge(graph, 5, 2);
    addEdge(graph, 5, 0);
    addEdge(graph, 4, 0);
    addEdge(graph, 4, 1);
    addEdge(graph, 2, 3);
    addEdge(graph, 3, 1);

    printf("Vertices in Topological Order:\n");
    topologicalSort(graph);

    return 0;
}
"""

def p5():
    return """#include <stdio.h>
#include <stdlib.h>

#define MAX_VERTICES 100

// Structure to represent a vertex in the graph
struct Vertex {
    int data;
    struct Vertex* next;
};

// Structure to represent a directed acyclic graph (DAG)
struct DAG {
    int numVertices;
    struct Vertex* adjacencyList[MAX_VERTICES];
    int* inDegree; // Array to store in-degrees of vertices
};

// Function to create a new vertex
struct Vertex* createVertex(int data) {
    struct Vertex* newVertex = (struct Vertex*)malloc(sizeof(struct Vertex));
    newVertex->data = data;
    newVertex->next = NULL;
    return newVertex;
}

// Function to create a new DAG with 'n' vertices
struct DAG* createDAG(int n) {
    struct DAG* graph = (struct DAG*)malloc(sizeof(struct DAG));
    graph->numVertices = n;
    for (int i = 0; i < n; i++) {
        graph->adjacencyList[i] = NULL;
    }
    graph->inDegree = (int*)calloc(n, sizeof(int));
    return graph;
}

// Function to add a directed edge from vertex 'from' to vertex 'to'
void addEdge(struct DAG* graph, int from, int to) {
    struct Vertex* newVertex = createVertex(to);
    newVertex->next = graph->adjacencyList[from];
    graph->adjacencyList[from] = newVertex;
    graph->inDegree[to]++;
}

// Function to perform topological sorting
void topologicalSort(struct DAG* graph) {
    int* visited = (int*)calloc(graph->numVertices, sizeof(int));
    int* stack = (int*)malloc(graph->numVertices * sizeof(int));
    int stackIndex = 0;

    // Function to perform DFS for topological sorting
    void topologicalSortDFS(int vertex) {
        visited[vertex] = 1;

        struct Vertex* adjVertex = graph->adjacencyList[vertex];
        while (adjVertex != NULL) {
            int adjData = adjVertex->data;
            if (!visited[adjData]) {
                topologicalSortDFS(adjData);
            }
            adjVertex = adjVertex->next;
        }

        stack[stackIndex] = vertex;
        stackIndex++;
    }

    for (int i = 0; i < graph->numVertices; i++) {
        if (!visited[i]) {
            topologicalSortDFS(i);
        }
    }

    printf("Topological Order: ");
    for (int i = stackIndex - 1; i >= 0; i--) {
        printf("%d ", stack[i]);
    }
    printf("\n");

    free(visited);
    free(stack);
}

int main() {
    struct DAG* graph = createDAG(6);

    addEdge(graph, 5, 2);
    addEdge(graph, 5, 0);
    addEdge(graph, 4, 0);
    addEdge(graph, 4, 1);
    addEdge(graph, 2, 3);
    addEdge(graph, 3, 1);

    printf("Vertices in Topological Order:\n");
    topologicalSort(graph);

    return 0;
}
"""

def p6():
    return """#include <stdio.h>
#include <string.h>

#define MAX 256 // Maximum character value

// Function to preprocess the bad character heuristic table
void preprocessBadCharHeuristic(char *pattern, int patternLength, int badCharHeuristic[MAX]) {
    for (int i = 0; i < MAX; i++) {
        badCharHeuristic[i] = patternLength;
    }

    for (int i = 0; i < patternLength - 1; i++) {
        badCharHeuristic[(int)pattern[i]] = patternLength - 1 - i;
    }
}

// Function to perform string matching using Horspool algorithm
void horspoolSearch(char *text, char *pattern) {
    int textLength = strlen(text);
    int patternLength = strlen(pattern);
    int badCharHeuristic[MAX];
    int shift = 0;

    // Preprocess the bad character heuristic table
    preprocessBadCharHeuristic(pattern, patternLength, badCharHeuristic);

    while (shift <= (textLength - patternLength)) {
        int j = patternLength - 1;

        while (j >= 0 && pattern[j] == text[shift + j]) {
            j--;
        }

        if (j < 0) {
            printf("Pattern found at index %d\n", shift);
            shift += badCharHeuristic[(int)text[shift + patternLength]];
        } else {
            shift += badCharHeuristic[(int)text[shift + patternLength]];
        }
    }
}

int main() {
    char text[] = "ABAAABCD";
    char pattern[] = "ABC";

    printf("Text: %s\n", text);
    printf("Pattern: %s\n", pattern);

    horspoolSearch(text, pattern);

    return 0;
}
"""

def p7():
    return """#include <stdio.h>
#include <limits.h>

#define V 5 // Number of vertices in the graph

// Function to find the vertex with the minimum key value, from the set of vertices not yet included in MST
int minKey(int key[], int mstSet[]) {
    int min = INT_MAX, min_index;

    for (int v = 0; v < V; v++) {
        if (!mstSet[v] && key[v] < min) {
            min = key[v];
            min_index = v;
        }
    }

    return min_index;
}

// Function to print the MST
void printMST(int parent[], int graph[V][V]) {
    printf("Edge   Weight\n");
    for (int i = 1; i < V; i++) {
        printf("%d - %d    %d \n", parent[i], i, graph[i][parent[i]]);
    }
}

// Function to find the MST using Prim's algorithm
void primMST(int graph[V][V]) {
    int parent[V]; // Array to store the constructed MST
    int key[V]; // Key values used to pick the minimum weight edge
    int mstSet[V]; // To represent set of vertices not yet included in MST

    for (int i = 0; i < V; i++) {
        key[i] = INT_MAX;
        mstSet[i] = 0;
    }

    key[0] = 0; // Start with the first vertex

    parent[0] = -1; // First node is always the root of MST

    for (int count = 0; count < V - 1; count++) {
        int u = minKey(key, mstSet);
        mstSet[u] = 1;

        for (int v = 0; v < V; v++) {
            if (graph[u][v] && !mstSet[v] && graph[u][v] < key[v]) {
                parent[v] = u;
                key[v] = graph[u][v];
            }
        }
    }

    // Print the MST
    printMST(parent, graph);
}

int main() {
    int graph[V][V] = {
        {0, 2, 0, 6, 0},
        {2, 0, 3, 8, 5},
        {0, 3, 0, 0, 7},
        {6, 8, 0, 0, 9},
        {0, 5, 7, 9, 0}
    };

    printf("Minimum Spanning Tree:\n");
    primMST(graph);

    return 0;
}
"""

def p8():
    return """#include <stdio.h>
#include <limits.h>

#define V 6 // Number of vertices in the graph

// Function to find the vertex with the minimum distance value, from the set of vertices not yet included in the shortest path tree
int minDistance(int dist[], int sptSet[]) {
    int min = INT_MAX, min_index;

    for (int v = 0; v < V; v++) {
        if (!sptSet[v] && dist[v] < min) {
            min = dist[v];
            min_index = v;
        }
    }

    return min_index;
}

// Function to print the shortest path from the source vertex to the destination vertex
void printPath(int parent[], int vertex) {
    if (parent[vertex] == -1) {
        printf("%d ", vertex);
        return;
    }
    printPath(parent, parent[vertex]);
    printf("-> %d ", vertex);
}

// Function to print the shortest distances from the source vertex to all other vertices
void printDijkstra(int dist[], int parent[], int src) {
    printf("Vertex   Shortest Distance   Shortest Path\n");
    for (int i = 0; i < V; i++) {
        printf("%d -> %d         %d                ", src, i, dist[i]);
        printPath(parent, i);
        printf("\n");
    }
}

// Function to find the shortest paths using Dijkstra's algorithm
void dijkstra(int graph[V][V], int src) {
    int dist[V]; // Array to store the shortest distance from the source vertex to each vertex
    int parent[V]; // Array to store the parent vertex in the shortest path tree
    int sptSet[V]; // Set to represent vertices included in the shortest path tree

    for (int i = 0; i < V; i++) {
        dist[i] = INT_MAX;
        parent[i] = -1;
        sptSet[i] = 0;
    }

    dist[src] = 0; // Distance to source vertex is always 0

    for (int count = 0; count < V - 1; count++) {
        int u = minDistance(dist, sptSet);
        sptSet[u] = 1;

        for (int v = 0; v < V; v++) {
            if (!sptSet[v] && graph[u][v] && dist[u] != INT_MAX && dist[u] + graph[u][v] < dist[v]) {
                dist[v] = dist[u] + graph[u][v];
                parent[v] = u;
            }
        }
    }

    printDijkstra(dist, parent, src);
}

int main() {
    int graph[V][V] = {
        {0, 2, 0, 0, 1, 0},
        {2, 0, 4, 0, 0, 0},
        {0, 4, 0, 3, 0, 0},
        {0, 0, 3, 0, 0, 5},
        {1, 0, 0, 0, 0, 4},
        {0, 0, 0, 5, 4, 0}
    };

    int sourceVertex = 0; // Change this to the desired source vertex (0-based index)

    printf("Shortest Paths from Vertex %d:\n", sourceVertex);
    dijkstra(graph, sourceVertex);

    return 0;
}
"""


def p9():
    return """#include <stdio.h>
#include <limits.h>

#define V 4 // Number of vertices in the graph

// Function to print the matrix
void printMatrix(int dist[V][V]) {
    printf("All Pair Shortest Paths Matrix:\n");
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            if (dist[i][j] == INT_MAX)
                printf("INF\t");
            else
                printf("%d\t", dist[i][j]);
        }
        printf("\n");
    }
}

// Function to find all pair shortest paths using Floyd's Algorithm
void floydWarshall(int graph[V][V]) {
    int dist[V][V];

    // Initialize the distance matrix with the graph
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            dist[i][j] = graph[i][j];
        }
    }

    // Update the distance matrix by considering all vertices as intermediates
    for (int k = 0; k < V; k++) {
        for (int i = 0; i < V; i++) {
            for (int j = 0; j < V; j++) {
                // If vertex k is on the shortest path from i to j and the path from i to k to j is shorter
                if (dist[i][k] != INT_MAX && dist[k][j] != INT_MAX && dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }

    printMatrix(dist);
}

int main() {
    int graph[V][V] = {
        {0, 5, INT_MAX, 10},
        {INT_MAX, 0, 3, INT_MAX},
        {INT_MAX, INT_MAX, 0, 1},
        {INT_MAX, INT_MAX, INT_MAX, 0}
    };

    floydWarshall(graph);

    return 0;
}
"""


def p10():
    return """#include <stdio.h>

// Function to find a subset with the given sum
int isSubsetSum(int set[], int n, int sum) {
    if (sum == 0) {
        return 1; // If sum is 0, an empty subset is found
    }
    if (n == 0) {
        return 0; // If there are no elements in the set, no subset can be found
    }

    // If the last element is greater than the sum, ignore it
    if (set[n - 1] > sum) {
        return isSubsetSum(set, n - 1, sum);
    }

    // Check if either of the following two cases is true:
    // 1. Include the last element in the subset and recur for the remaining sum and elements
    // 2. Exclude the last element and recur for the remaining elements
    return isSubsetSum(set, n - 1, sum) || isSubsetSum(set, n - 1, sum - set[n - 1]);
}

int main() {
    int set[] = {3, 34, 4, 12, 5, 2};
    int n = sizeof(set) / sizeof(set[0]);
    int sum = 9;

    if (isSubsetSum(set, n, sum)) {
        printf("Subset with sum %d exists.\n", sum);
    } else {
        printf("Subset with sum %d does not exist.\n", sum);
    }

    return 0;
}
"""

