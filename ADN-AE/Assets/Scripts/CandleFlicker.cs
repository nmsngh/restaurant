using UnityEngine;

public class CandleFlicker : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float swayAmount = 0.0000001f;    // 좌우 흔들림 정도
    [SerializeField] private float swaySpeed = 2.0f;     // 기본 흔들림 속도

    [Header("Random Movement")]
    [SerializeField] private float randomMovementAmount = 0.05f;  // 불규칙한 움직임 정도
    [SerializeField] private float randomMovementSpeed = 0.2f;    // 불규칙한 움직임 속도

    [Header("Rotation Settings")]
    [SerializeField] private float tiltAmount = 5.0f;    // 기울어짐 정도
    [SerializeField] private float rotationSpeed = 1.5f; // 회전 속도

    // 원래 위치와 회전값 저장
    private Vector3 startPosition;
    private Quaternion startRotation;

    // 노이즈 오프셋 (각각 다른 움직임을 위한 랜덤값)
    private float noiseOffset1;
    private float noiseOffset2;
    private float noiseOffset3;

    private void Start()
    {
        // 시작 위치와 회전값 저장
        startPosition = transform.localPosition;
        startRotation = transform.localRotation;        
        // 랜덤한 시작점 설정 (각각 다른 촛불이 다르게 움직이도록)
        noiseOffset1 = Random.Range(0f, 100f);
        noiseOffset2 = Random.Range(0f, 100f);
        noiseOffset3 = Random.Range(0f, 100f);                
    }

    private void Update()
    {
        // 시간에 따른 기본 사인 웨이브 움직임
        float sineWave = Mathf.Sin(Time.time * swaySpeed);

        // Perlin 노이즈를 이용한 불규칙한 움직임
        float noiseX = Mathf.PerlinNoise(Time.time * randomMovementSpeed, noiseOffset1) - 0.5f;
        float noiseY = Mathf.PerlinNoise(Time.time * randomMovementSpeed, noiseOffset2) - 0.5f;
        float noiseZ = Mathf.PerlinNoise(Time.time * randomMovementSpeed, noiseOffset3) - 0.5f;

        // 위치 계산
        Vector3 newPosition = startPosition;
        newPosition.x += sineWave * swayAmount;  // 좌우 흔들림
        newPosition += new Vector3(
            noiseX * randomMovementAmount,
            noiseY * randomMovementAmount,
            noiseZ * randomMovementAmount
        );

        // 회전 계산
        Vector3 rotationOffset = new Vector3(
            noiseX * tiltAmount,
            noiseY * tiltAmount,
            sineWave * tiltAmount
        );

        // 위치와 회전 적용
        transform.localPosition = newPosition;
        transform.localRotation = startRotation * Quaternion.Euler(rotationOffset);
    }

    // 게임 실행 중 파라미터 수정을 위한 public 메서드들
    public void SetSwayAmount(float amount) => swayAmount = amount;
    public void SetSwaySpeed(float speed) => swaySpeed = speed;
    public void SetRandomMovement(float amount) => randomMovementAmount = amount;
    public void SetTiltAmount(float amount) => tiltAmount = amount;
}