# Interview Ready Service - Flutter Integration Guide

## 📋 Información General

### URL Base del Servicio
```
https://teching.tech/interviewready
```

### Autenticación
- **Tipo:** JWT Bearer Token
- **Header requerido:** `Authorization: Bearer <token>`
- **Prefijo de rutas:** `/api/v1`

---

## 🔐 Configuración de Autenticación

### Headers Requeridos
```dart
Map<String, String> getHeaders(String token) {
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $token',
    'Accept': 'application/json',
  };
}
```

### Ejemplo de Cliente HTTP
```dart
class InterviewReadyApiClient {
  static const String baseUrl = 'https://teching.tech/interviewready/api/v1';
  final http.Client _client = http.Client();
  
  Future<Map<String, dynamic>> makeRequest({
    required String endpoint,
    required String method,
    required String token,
    Map<String, dynamic>? body,
    Map<String, String>? queryParams,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint').replace(
      queryParameters: queryParams,
    );
    
    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
      'Accept': 'application/json',
    };
    
    http.Response response;
    
    switch (method.toLowerCase()) {
      case 'get':
        response = await _client.get(uri, headers: headers);
        break;
      case 'post':
        response = await _client.post(
          uri,
          headers: headers,
          body: body != null ? json.encode(body) : null,
        );
        break;
      case 'put':
        response = await _client.put(
          uri,
          headers: headers,
          body: body != null ? json.encode(body) : null,
        );
        break;
      default:
        throw Exception('Método HTTP no soportado: $method');
    }
    
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        statusCode: response.statusCode,
        message: response.body,
      );
    }
  }
}
```

---

## 📚 Endpoints Disponibles

### 1. Generar Preguntas de Entrevista
**POST** `/interview/questions/generate`

#### Request Body:
```json
{
  "user_id": "string",
  "user_seniority": "junior|mid|senior|lead|principal",
  "user_specialization": "string",
  "question_number": {
    "value": 5
  },
  "interview_type": "behavioral|structured|technical|simulation"
}
```

#### Dart Model:
```dart
class CreateInterviewRequest {
  final String userId;
  final String userSeniority;
  final String userSpecialization;
  final QuestionCount questionNumber;
  final String interviewType;

  CreateInterviewRequest({
    required this.userId,
    required this.userSeniority,
    required this.userSpecialization,
    required this.questionNumber,
    this.interviewType = 'behavioral',
  });

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'user_seniority': userSeniority,
    'user_specialization': userSpecialization,
    'question_number': questionNumber.toJson(),
    'interview_type': interviewType,
  };
}

class QuestionCount {
  final int value; // 5, 10, 15, 30

  QuestionCount({required this.value});

  Map<String, dynamic> toJson() => {
    'value': value,
  };
}
```

#### Response:
```json
{
  "id": "string",
  "user_id": "string",
  "current_question": {
    "id": 1,
    "question": "string",
    "answer": null,
    "feedback": null,
    "competency": "string",
    "difficulty": "easy|medium|hard"
  },
  "next_question": {
    "id": 2,
    "question": "string",
    "answer": null,
    "feedback": null,
    "competency": "string",
    "difficulty": "easy|medium|hard"
  },
  "init_at": "2025-01-27T10:30:00Z",
  "status": "in_progress",
  "question_number": 5,
  "actual_question": 1
}
```

#### Dart Implementation:
```dart
Future<CreateInterviewResponse> generateQuestions({
  required String token,
  required CreateInterviewRequest request,
}) async {
  final response = await makeRequest(
    endpoint: '/interview/questions/generate',
    method: 'POST',
    token: token,
    body: request.toJson(),
  );
  
  return CreateInterviewResponse.fromJson(response);
}
```

### 2. Responder Pregunta
**POST** `/interview/{interview_id}/response`

#### Request Body:
```json
{
  "user_response": "string",
  "user_id": "string"
}
```

#### Dart Model:
```dart
class AnswerQuestionRequest {
  final String userResponse;
  final String userId;

  AnswerQuestionRequest({
    required this.userResponse,
    required this.userId,
  });

  Map<String, dynamic> toJson() => {
    'user_response': userResponse,
    'user_id': userId,
  };
}
```

#### Response:
```json
{
  "id": "string",
  "user_id": "string",
  "current_question": {
    "id": 1,
    "question": "string",
    "answer": "string",
    "feedback": "string",
    "competency": "string",
    "difficulty": "easy"
  },
  "next_question": {
    "id": 2,
    "question": "string",
    "answer": null,
    "feedback": null,
    "competency": "string",
    "difficulty": "medium"
  },
  "init_at": "2025-01-27T10:30:00Z",
  "status": "in_progress",
  "question_number": 5,
  "actual_question": 2,
  "feedback": "string",
  "good_question": true
}
```

#### Dart Implementation:
```dart
Future<CreateInterviewResponse> answerQuestion({
  required String token,
  required String interviewId,
  required AnswerQuestionRequest request,
}) async {
  final response = await makeRequest(
    endpoint: '/interview/$interviewId/response',
    method: 'POST',
    token: token,
    body: request.toJson(),
  );
  
  return CreateInterviewResponse.fromJson(response);
}
```

### 3. Obtener Entrevista por ID
**GET** `/interview/{interview_id}`

#### Response:
```json
{
  "id": "string",
  "userId": "string",
  "user_seniority": "string",
  "user_specialization": "string",
  "interview_type": "behavioral",
  "questions": [
    {
      "id": 1,
      "question": "string",
      "answer": "string",
      "feedback": "string",
      "competency": "string",
      "difficulty": "easy"
    }
  ],
  "init_at": "2025-01-27T10:30:00Z",
  "end_at": "2025-01-27T11:00:00Z",
  "status": "completed",
  "question_number": 5,
  "actual_question": {
    "id": 5,
    "question": "string",
    "answer": "string",
    "feedback": "string",
    "competency": "string",
    "difficulty": "hard"
  },
  "points_earned": 8,
  "feedback": {
    "overall_score": 75,
    "competency_breakdown": [
      {
        "name": "leadership",
        "score": 80
      }
    ],
    "points_earned": 8,
    "focus_questions": ["question text"],
    "summary_feedback": "string"
  }
}
```

#### Dart Implementation:
```dart
Future<InterviewReady> getInterviewById({
  required String token,
  required String interviewId,
}) async {
  final response = await makeRequest(
    endpoint: '/interview/$interviewId',
    method: 'GET',
    token: token,
  );
  
  return InterviewReady.fromJson(response);
}
```

### 4. Obtener Historial de Entrevistas
**GET** `/interview/history/{user_id}`

#### Query Parameters:
- `limit` (opcional): int, default 100
- `skip` (opcional): int, default 0

#### Response:
```json
{
  "interviews": [
    {
      "id": "string",
      "userId": "string",
      "user_seniority": "string",
      "user_specialization": "string",
      "init_at": "2025-01-27T10:30:00Z",
      "end_at": "2025-01-27T11:00:00Z",
      "status": "completed",
      "question_number": 5,
      "points_earned": 8
    }
  ],
  "total_count": 1,
  "user_id": "string",
  "status_filter": "completed"
}
```

#### Dart Implementation:
```dart
Future<InterviewHistoryResponse> getInterviewHistory({
  required String token,
  required String userId,
  int limit = 100,
  int skip = 0,
}) async {
  final response = await makeRequest(
    endpoint: '/interview/history/$userId',
    method: 'GET',
    token: token,
    queryParams: {
      'limit': limit.toString(),
      'skip': skip.toString(),
    },
  );
  
  return InterviewHistoryResponse.fromJson(response);
}
```

### 5. Generar Feedback Final
**POST** `/interview/{interview_id}/feedback`

#### Response:
```json
{
  "overall_score": 75,
  "competency_breakdown": [
    {
      "name": "leadership",
      "score": 80
    },
    {
      "name": "collaboration",
      "score": 70
    }
  ],
  "points_earned": 8,
  "focus_questions": [
    "Tell me about a time when you had to lead a cross-functional team"
  ],
  "summary_feedback": "You demonstrated strong technical skills and problem-solving abilities. Consider providing more specific metrics and quantifiable results in your examples."
}
```

#### Dart Implementation:
```dart
Future<FeedbackResponse> generateFinalFeedback({
  required String token,
  required String interviewId,
}) async {
  final response = await makeRequest(
    endpoint: '/interview/$interviewId/feedback',
    method: 'POST',
    token: token,
  );
  
  return FeedbackResponse.fromJson(response);
}
```

---

## 🎯 Modelos de Datos Dart

### Modelos Principales:
```dart
class Question {
  final int id;
  final String question;
  final String? answer;
  final String? feedback;
  final String? competency;
  final String? difficulty;

  Question({
    required this.id,
    required this.question,
    this.answer,
    this.feedback,
    this.competency,
    this.difficulty,
  });

  factory Question.fromJson(Map<String, dynamic> json) => Question(
    id: json['id'],
    question: json['question'],
    answer: json['answer'],
    feedback: json['feedback'],
    competency: json['competency'],
    difficulty: json['difficulty'],
  );
}

class InterviewReady {
  final String id;
  final String userId;
  final String userSeniority;
  final String userSpecialization;
  final String interviewType;
  final List<Question> questions;
  final DateTime initAt;
  final DateTime? endAt;
  final String status;
  final int questionNumber;
  final Question? actualQuestion;
  final int pointsEarned;
  final FeedbackResponse? feedback;

  InterviewReady({
    required this.id,
    required this.userId,
    required this.userSeniority,
    required this.userSpecialization,
    required this.interviewType,
    required this.questions,
    required this.initAt,
    this.endAt,
    required this.status,
    required this.questionNumber,
    this.actualQuestion,
    required this.pointsEarned,
    this.feedback,
  });

  factory InterviewReady.fromJson(Map<String, dynamic> json) => InterviewReady(
    id: json['id'],
    userId: json['userId'],
    userSeniority: json['user_seniority'],
    userSpecialization: json['user_specialization'],
    interviewType: json['interview_type'],
    questions: (json['questions'] as List)
        .map((q) => Question.fromJson(q))
        .toList(),
    initAt: DateTime.parse(json['init_at']),
    endAt: json['end_at'] != null ? DateTime.parse(json['end_at']) : null,
    status: json['status'],
    questionNumber: json['question_number'],
    actualQuestion: json['actual_question'] != null 
        ? Question.fromJson(json['actual_question']) 
        : null,
    pointsEarned: json['points_earned'],
    feedback: json['feedback'] != null 
        ? FeedbackResponse.fromJson(json['feedback']) 
        : null,
  );
}

class CreateInterviewResponse {
  final String id;
  final String userId;
  final Question currentQuestion;
  final Question? nextQuestion;
  final DateTime initAt;
  final String status;
  final int questionNumber;
  final int actualQuestion;
  final String? feedback;
  final bool? goodQuestion;
  final String? message;

  CreateInterviewResponse({
    required this.id,
    required this.userId,
    required this.currentQuestion,
    this.nextQuestion,
    required this.initAt,
    required this.status,
    required this.questionNumber,
    required this.actualQuestion,
    this.feedback,
    this.goodQuestion,
    this.message,
  });

  factory CreateInterviewResponse.fromJson(Map<String, dynamic> json) => 
      CreateInterviewResponse(
    id: json['id'],
    userId: json['user_id'],
    currentQuestion: Question.fromJson(json['current_question']),
    nextQuestion: json['next_question'] != null 
        ? Question.fromJson(json['next_question']) 
        : null,
    initAt: DateTime.parse(json['init_at']),
    status: json['status'],
    questionNumber: json['question_number'],
    actualQuestion: json['actual_question'],
    feedback: json['feedback'],
    goodQuestion: json['good_question'],
    message: json['message'],
  );
}

class FeedbackResponse {
  final int overallScore;
  final List<CompetencyBreakdown> competencyBreakdown;
  final int pointsEarned;
  final List<String> focusQuestions;
  final String summaryFeedback;

  FeedbackResponse({
    required this.overallScore,
    required this.competencyBreakdown,
    required this.pointsEarned,
    required this.focusQuestions,
    required this.summaryFeedback,
  });

  factory FeedbackResponse.fromJson(Map<String, dynamic> json) => 
      FeedbackResponse(
    overallScore: json['overall_score'],
    competencyBreakdown: (json['competency_breakdown'] as List)
        .map((c) => CompetencyBreakdown.fromJson(c))
        .toList(),
    pointsEarned: json['points_earned'],
    focusQuestions: List<String>.from(json['focus_questions']),
    summaryFeedback: json['summary_feedback'],
  );
}

class CompetencyBreakdown {
  final String name;
  final int score;

  CompetencyBreakdown({
    required this.name,
    required this.score,
  });

  factory CompetencyBreakdown.fromJson(Map<String, dynamic> json) => 
      CompetencyBreakdown(
    name: json['name'],
    score: json['score'],
  );
}
```

---

## ⚠️ Manejo de Errores

### Códigos de Estado HTTP
- **200**: Éxito
- **400**: Bad Request - Datos inválidos
- **401**: Unauthorized - Token inválido o expirado
- **404**: Not Found - Recurso no encontrado
- **500**: Internal Server Error - Error del servidor

### Clase de Excepción Personalizada:
```dart
class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException({
    required this.statusCode,
    required this.message,
  });

  @override
  String toString() => 'ApiException: $statusCode - $message';
}

// Manejo de errores común
Future<T> handleApiCall<T>(Future<T> Function() apiCall) async {
  try {
    return await apiCall();
  } on ApiException catch (e) {
    switch (e.statusCode) {
      case 401:
        // Redirigir a login o renovar token
        throw Exception('Token expirado. Por favor, inicia sesión nuevamente.');
      case 404:
        throw Exception('Recurso no encontrado.');
      case 500:
        throw Exception('Error interno del servidor. Inténtalo más tarde.');
      default:
        throw Exception('Error: ${e.message}');
    }
  } catch (e) {
    throw Exception('Error de conexión: $e');
  }
}
```

---

## 🔄 Flujo de Uso Recomendado

### 1. Crear Nueva Entrevista:
```dart
// 1. Generar preguntas
final interview = await generateQuestions(
  token: userToken,
  request: CreateInterviewRequest(
    userId: currentUserId,
    userSeniority: 'mid',
    userSpecialization: 'Frontend Development',
    questionNumber: QuestionCount(value: 10),
    interviewType: 'behavioral',
  ),
);

// 2. Mostrar primera pregunta
showQuestion(interview.currentQuestion);
```

### 2. Responder Preguntas:
```dart
// Loop para cada respuesta
final response = await answerQuestion(
  token: userToken,
  interviewId: interview.id,
  request: AnswerQuestionRequest(
    userResponse: userAnswer,
    userId: currentUserId,
  ),
);

if (response.status == 'completed') {
  // Entrevista terminada
  showFinalResults(response);
} else {
  // Mostrar siguiente pregunta
  showQuestion(response.nextQuestion!);
  showFeedback(response.feedback, response.goodQuestion);
}
```

### 3. Ver Historial:
```dart
final history = await getInterviewHistory(
  token: userToken,
  userId: currentUserId,
  limit: 20,
  skip: 0,
);

showInterviewHistory(history.interviews);
```

---

## 📱 Consideraciones para Flutter

### Dependencias Recomendadas:
```yaml
dependencies:
  http: ^1.1.0
  shared_preferences: ^2.2.2
  provider: ^6.1.1
```

### Gestión de Estado:
```dart
class InterviewProvider extends ChangeNotifier {
  final InterviewReadyApiClient _apiClient = InterviewReadyApiClient();
  
  InterviewReady? _currentInterview;
  Question? _currentQuestion;
  bool _isLoading = false;
  
  InterviewReady? get currentInterview => _currentInterview;
  Question? get currentQuestion => _currentQuestion;
  bool get isLoading => _isLoading;
  
  Future<void> startInterview(CreateInterviewRequest request) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await _apiClient.generateQuestions(
        token: await getStoredToken(),
        request: request,
      );
      _currentQuestion = response.currentQuestion;
      notifyListeners();
    } catch (e) {
      // Manejar error
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
```

---

## 🚀 Testing

### Ejemplo de Test de Integración:
```dart
void main() {
  group('Interview Ready API Tests', () {
    late InterviewReadyApiClient client;
    const testToken = 'your-test-jwt-token';
    
    setUp(() {
      client = InterviewReadyApiClient();
    });
    
    test('should generate questions successfully', () async {
      final request = CreateInterviewRequest(
        userId: 'test-user',
        userSeniority: 'mid',
        userSpecialization: 'Flutter Development',
        questionNumber: QuestionCount(value: 5),
        interviewType: 'behavioral',
      );
      
      final response = await client.generateQuestions(
        token: testToken,
        request: request,
      );
      
      expect(response.id, isNotNull);
      expect(response.currentQuestion, isNotNull);
      expect(response.status, equals('in_progress'));
    });
  });
}
```

---

## 📞 Soporte

### Contacto del Equipo Backend:
- **Documentación API**: https://teching.tech/interviewready/docs
- **Ambiente de Testing**: https://teching.tech/interviewready/health

### URLs de Prueba:
- **Health Check**: `GET https://teching.tech/interviewready/`
- **API Docs**: `GET https://teching.tech/interviewready/docs`

---

> **Nota**: Asegúrate de manejar adecuadamente la renovación de tokens JWT y implementar retry logic para llamadas de red fallidas.
