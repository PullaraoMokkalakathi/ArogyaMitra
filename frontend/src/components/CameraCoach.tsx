import { useEffect, useRef, useCallback } from "react";
import { Pose, Results, POSE_CONNECTIONS } from "@mediapipe/pose";
import { Camera } from "@mediapipe/camera_utils";
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { calculateAccuracy } from "../utils/workoutAccuracy";

export type ExerciseType = "Pushups" | "Squats" | "Planks" | "Lunges" | "Bench Press" | "Deadlift" | "Bicep Curl" | "Hammer Curl" | "Cable Crossovers" | "Seated Cable Row" | "Lat Pulldown" | "Tricep Pushdown" | "Calf Raises" | "Reverse Pec Deck" | "Shoulder Press" | "Russian Twists" | "Lateral Raises" | "Chest Fly" | string;

interface CameraCoachProps {
  exercise: ExerciseType;
  onUpdateScore: (score: number) => void;
  onUpdateReps: (reps: number) => void;
  onUpdateFeedback: (feedback: string) => void;
}

function calculateAngle(a: {x: number, y: number}, b: {x: number, y: number}, c: {x: number, y: number}) {
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
  let angle = Math.abs((radians * 180.0) / Math.PI);
  if (angle > 180.0) {
    angle = 360 - angle;
  }
  return angle;
}

export default function CameraCoach({ exercise, onUpdateScore, onUpdateReps, onUpdateFeedback }: CameraCoachProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // State refs for animation loops to access current values without closing over stale state
  const exerciseRef = useRef(exercise);
  const repCountRef = useRef(0);
  const stageRef = useRef("up");
  const lastUpdateRef = useRef(Date.now());
  const cameraRef = useRef<Camera | null>(null);

  // Prevent spamming React state every frame
  const lastFeedbackRef = useRef("");
  const updateFeedback = useCallback((msg: string) => {
    if (lastFeedbackRef.current !== msg) {
      lastFeedbackRef.current = msg;
      onUpdateFeedback(msg);
    }
  }, [onUpdateFeedback]);

  const scoreRef = useRef(100);
  const updateScore = useCallback((score: number) => {
    if (scoreRef.current !== score) {
      scoreRef.current = score;
      onUpdateScore(score);
    }
  }, [onUpdateScore]);

  const updateScoreFromAngle = useCallback((angle: number, workoutName: string) => {
    const accuracy = calculateAccuracy(angle, workoutName);
    updateScore(accuracy);
  }, [updateScore]);

  useEffect(() => {
    exerciseRef.current = exercise;
    repCountRef.current = 0;
    stageRef.current = "up";
    onUpdateReps(0);
    updateFeedback("Ready to start");
  }, [exercise, onUpdateReps, updateFeedback]);

  const onResults = useCallback((results: Results) => {
    if (!canvasRef.current || !videoRef.current) return;

    const canvasCtx = canvasRef.current.getContext("2d");
    if (!canvasCtx) return;

    lastUpdateRef.current = Date.now();

    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    
    canvasCtx.drawImage(results.image, 0, 0, canvasRef.current.width, canvasRef.current.height);

    const landmarks = results.poseLandmarks;

    if (!landmarks || landmarks.length === 0) {
      updateFeedback("Move into frame");
      canvasCtx.restore();
      return;
    }

    let visibleLandmarks = 0;
    for (let lm of landmarks) {
      if (lm.visibility && lm.visibility > 0.5) visibleLandmarks++;
    }

    if (visibleLandmarks < 12) {
      updateFeedback("Move into camera frame");
      canvasCtx.restore();
      return;
    }

    drawConnectors(canvasCtx, landmarks, POSE_CONNECTIONS, { color: '#00FFFF', lineWidth: 4 });
    drawLandmarks(canvasCtx, landmarks, { color: '#FF00FF', lineWidth: 2, radius: 3 });

    try {
      const ex = exerciseRef.current.toLowerCase();
      
      // Pushups
      if (ex.includes("pushup") || ex.includes("push-up")) {
        const shoulder = landmarks[11];
        const elbow = landmarks[13];
        const wrist = landmarks[15];
        const hip = landmarks[23];
        const ankle = landmarks[27];

        if (shoulder.visibility! > 0.7 && elbow.visibility! > 0.7 && wrist.visibility! > 0.7 && hip.visibility! > 0.7) {
          const elbowAngle = calculateAngle(shoulder, elbow, wrist);
          const bodyAngle = calculateAngle(shoulder, hip, ankle);

          // Proper rep counting: up -> down -> up cycle
          if (elbowAngle > 160) {
            stageRef.current = "up";
            if (bodyAngle >= 160 && bodyAngle <= 185) {
              updateFeedback("Perfect form 💪");
            } else {
              updateFeedback("Keep body straight");
            }
          } else if (elbowAngle < 90 && stageRef.current === "up") {
            stageRef.current = "down";
            if (bodyAngle >= 160 && bodyAngle <= 185) {
              updateFeedback("Good depth");
            } else {
              updateFeedback("Keep body straight");
            }
          } else if (elbowAngle > 160 && stageRef.current === "down") {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          } else if (elbowAngle >= 90 && elbowAngle <= 160) {
            updateFeedback("Go lower");
          }
          
          updateScoreFromAngle(elbowAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Squats
      else if (ex.includes("squat")) {
        const hip = landmarks[24];
        const knee = landmarks[26];
        const ankle = landmarks[28];
        const shoulder = landmarks[12];

        if (hip.visibility! > 0.7 && knee.visibility! > 0.7 && ankle.visibility! > 0.7 && shoulder.visibility! > 0.7) {
          const kneeAngle = calculateAngle(hip, knee, ankle);
          const backAngle = calculateAngle(shoulder, hip, knee);

          // Proper rep counting: up -> down -> up cycle
          if (kneeAngle > 160 && backAngle >= 150) {
            stageRef.current = "up";
            updateFeedback("Ready - go down");
          } else if (kneeAngle < 90 && stageRef.current === "up" && backAngle >= 150) {
            stageRef.current = "down";
            updateFeedback("Good depth - rise up");
          } else if (kneeAngle > 160 && stageRef.current === "down" && backAngle >= 150) {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          } else if (kneeAngle >= 90 && kneeAngle <= 160 && stageRef.current === "up" && backAngle >= 150) {
            updateFeedback("Go lower");
          } else if (backAngle < 150) {
            updateFeedback("Chest up - straight back");
          } else if (kneeAngle < 90) {
            updateFeedback("Knee alignment");
          }
          
          updateScoreFromAngle(kneeAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Plank
      else if (ex.includes("plank")) {
        const shoulder = landmarks[11];
        const hip = landmarks[23];
        const ankle = landmarks[27];

        if (shoulder.visibility! > 0.7 && hip.visibility! > 0.7 && ankle.visibility! > 0.7) {
          const bodyAngle = calculateAngle(shoulder, hip, ankle);
          
          if (bodyAngle >= 160 && bodyAngle <= 190) {
            updateFeedback("Perfect plank 💪");
          } else if (bodyAngle < 160) {
            updateFeedback("Raise hips");
          } else if (bodyAngle > 190) {
            updateFeedback("Lower hips");
          }
          
          updateScoreFromAngle(bodyAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Lunges
      else if (ex.includes("lunge")) {
        const hip = landmarks[24];
        const knee = landmarks[26];
        const ankle = landmarks[28];
        const shoulder = landmarks[12];

        if (hip.visibility! > 0.7 && knee.visibility! > 0.7 && ankle.visibility! > 0.7 && shoulder.visibility! > 0.7) {
          const kneeAngle = calculateAngle(hip, knee, ankle);
          const bodyAngle = calculateAngle(shoulder, hip, knee);

          // Proper rep counting: up -> down -> up cycle
          if (kneeAngle > 160 && bodyAngle >= 150) {
            stageRef.current = "up";
            updateFeedback("Step forward");
          } else if (kneeAngle < 100 && stageRef.current === "up" && bodyAngle >= 150) {
            stageRef.current = "down";
            updateFeedback("Good depth");
          } else if (kneeAngle > 160 && stageRef.current === "down" && bodyAngle >= 150) {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          } else if (bodyAngle < 150) {
            updateFeedback("Straight back");
          }
          
          updateScoreFromAngle(kneeAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Bench Press
      else if (ex.includes("bench press")) {
        const shoulder = landmarks[11];
        const elbow = landmarks[13];
        const wrist = landmarks[15];

        if (shoulder.visibility! > 0.7 && elbow.visibility! > 0.7 && wrist.visibility! > 0.7) {
          const elbowAngle = calculateAngle(shoulder, elbow, wrist);

          // Proper rep counting: up -> down -> up cycle
          if (elbowAngle > 160) {
            stageRef.current = "up";
            updateFeedback("Ready - lower slowly");
          } else if (elbowAngle < 90 && stageRef.current === "up") {
            stageRef.current = "down";
            updateFeedback("Good press");
          } else if (elbowAngle > 160 && stageRef.current === "down") {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          } else if (elbowAngle >= 90 && elbowAngle <= 160 && stageRef.current === "up") {
            updateFeedback("Control the movement");
          }
          
          updateScoreFromAngle(elbowAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Deadlift
      else if (ex.includes("deadlift")) {
        const shoulder = landmarks[11];
        const hip = landmarks[23];
        const knee = landmarks[25];

        if (shoulder.visibility! > 0.7 && hip.visibility! > 0.7 && knee.visibility! > 0.7) {
          const hipAngle = calculateAngle(shoulder, hip, knee);

          // Proper rep counting: up -> down -> up cycle
          if (hipAngle > 160) {
            stageRef.current = "up";
            updateFeedback("Ready - hinge at hips");
          } else if (hipAngle < 100 && stageRef.current === "up") {
            stageRef.current = "down";
            updateFeedback("Good lift");
          } else if (hipAngle > 160 && stageRef.current === "down") {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          } else if (hipAngle >= 100 && hipAngle <= 160 && stageRef.current === "up") {
            updateFeedback("Lower hips");
          }
          
          updateScoreFromAngle(hipAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Bicep Curl / Hammer Curl
      else if (ex.includes("bicep curl") || ex.includes("hammer curl")) {
        const shoulder = landmarks[11];
        const elbow = landmarks[13];
        const wrist = landmarks[15];

        if (shoulder.visibility! > 0.7 && elbow.visibility! > 0.7 && wrist.visibility! > 0.7) {
          const elbowAngle = calculateAngle(shoulder, elbow, wrist);

          // Proper rep counting: up -> down -> up cycle
          if (elbowAngle > 160) {
            stageRef.current = "up";
            updateFeedback("Full extension");
          } else if (elbowAngle < 50 && stageRef.current === "up") {
            stageRef.current = "down";
            updateFeedback("Good contraction 💪");
          } else if (elbowAngle > 160 && stageRef.current === "down") {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          } else if (elbowAngle >= 50 && elbowAngle <= 160 && stageRef.current === "up") {
            updateFeedback("Control movement");
          }
          
          updateScoreFromAngle(elbowAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Lat Pulldown / Seated Cable Row / Tricep Pushdown
      else if (ex.includes("lat pulldown") || ex.includes("cable row") || ex.includes("tricep pushdown") || ex.includes("tricep push down")) {
        const shoulder = landmarks[11];
        const elbow = landmarks[13];
        const wrist = landmarks[15];

        if (shoulder.visibility! > 0.7 && elbow.visibility! > 0.7 && wrist.visibility! > 0.7) {
          const elbowAngle = calculateAngle(shoulder, elbow, wrist);

          // Proper rep counting: up -> down -> up cycle
          if (elbowAngle > 160) {
            stageRef.current = "up";
            updateFeedback("Full extension");
          } else if (elbowAngle < 90 && stageRef.current === "up") {
            stageRef.current = "down";
            if (elbowAngle < 70) {
              updateFeedback("Full contraction 💪");
            } else {
              updateFeedback("Control movement");
            }
          } else if (elbowAngle > 160 && stageRef.current === "down") {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          } else if (elbowAngle >= 90 && elbowAngle <= 160 && stageRef.current === "up") {
            updateFeedback("Pull/push lower");
          }
          
          updateScoreFromAngle(elbowAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Shoulder Press / Lateral Raises / Reverse Pec Deck / Chest Fly
      else if (ex.includes("shoulder press") || ex.includes("lateral raise") || ex.includes("pec deck") || ex.includes("chest fly")) {
        const shoulder = landmarks[11];
        const elbow = landmarks[13];
        const wrist = landmarks[15];

        if (shoulder.visibility! > 0.7 && elbow.visibility! > 0.7 && wrist.visibility! > 0.7) {
          const shoulderAngle = calculateAngle(landmarks[12], shoulder, elbow);
          const elbowAngle = calculateAngle(shoulder, elbow, wrist);

          // Proper rep counting: up -> down -> up cycle
          if (elbowAngle > 160) {
            stageRef.current = "up";
            updateFeedback("Arms down - ready");
          } else if (elbowAngle < 90 && stageRef.current === "up" && shoulderAngle > 150) {
            stageRef.current = "down";
            updateFeedback("Good height 💪");
          } else if (elbowAngle > 160 && stageRef.current === "down") {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          } else if (elbowAngle >= 90 && elbowAngle <= 160 && stageRef.current === "up") {
            updateFeedback("Raise higher");
          }
          
          updateScoreFromAngle(elbowAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Calf Raises
      else if (ex.includes("calf raise")) {
        const hip = landmarks[24];
        const knee = landmarks[26];
        const ankle = landmarks[28];

        if (hip.visibility! > 0.7 && knee.visibility! > 0.7 && ankle.visibility! > 0.7) {
          const kneeAngle = calculateAngle(hip, knee, ankle);

          // Proper rep counting: up -> down -> up cycle
          if (kneeAngle < 160) {
            stageRef.current = "down";
            updateFeedback("Rise up");
          } else if (kneeAngle > 170 && stageRef.current === "down") {
            stageRef.current = "up";
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
            updateFeedback("Rep complete 💪");
          }
          
          updateScoreFromAngle(kneeAngle, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      // Russian Twists
      else if (ex.includes("russian twist")) {
        const shoulder = landmarks[11];
        const hip = landmarks[23];

        if (shoulder.visibility! > 0.7 && hip.visibility! > 0.7) {
          // For Russian twists, we track shoulder-hip rotation
          const torsoTilt = Math.abs(shoulder.x - hip.x) * 100;
          
          if (torsoTilt < 20) {
            stageRef.current = "up";
            updateFeedback("Hold position");
          } else if (torsoTilt > 35 && stageRef.current === "up") {
            stageRef.current = "down";
            updateFeedback("Good twist 💪");
            repCountRef.current += 1;
            onUpdateReps(repCountRef.current);
          }
          
          updateScoreFromAngle(torsoTilt, exerciseRef.current);
        } else {
          updateFeedback("Move into camera frame");
        }
      }
      else {
        updateFeedback("Tracking general movement");
      }
    } catch (error) {
      console.error(error);
    }

    canvasCtx.restore();
  }, [onUpdateReps, updateFeedback, updateScoreFromAngle]);

  useEffect(() => {
    let active = true;

    const initPose = async () => {
      const pose = new Pose({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
        },
      });

      pose.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        smoothSegmentation: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      pose.onResults((results) => {
        if (active) onResults(results);
      });

      if (videoRef.current) {
        const camera = new Camera(videoRef.current, {
          onFrame: async () => {
            if (videoRef.current && active) {
              await pose.send({ image: videoRef.current });
            }
          },
          width: 640,
          height: 480,
        });
        camera.start();
        cameraRef.current = camera;
      }
    };

    initPose();

    // Auto pause inactivity checking
    const inactivityInterval = setInterval(() => {
      const now = Date.now();
      if (now - lastUpdateRef.current > 5000) {
        updateFeedback("Auto-paused (Inactivity)");
      }
    }, 2000);

    return () => {
      active = false;
      clearInterval(inactivityInterval);
      if (cameraRef.current) {
        cameraRef.current.stop();
      }
    };
  }, [onResults, updateFeedback]);

  return (
    <div className="relative w-full overflow-hidden rounded-2xl bg-black aspect-video border border-white/10 shadow-lg">
      {/* Hidden Video element for MediaPipe processing */}
      <video ref={videoRef} className="hidden" playsInline />
      
      {/* Canvas for rendering with skeleton */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 h-full w-full object-cover"
        width={640}
        height={480}
      />
      
      {/* Target Crosshair Overlay for aesthetics */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center opacity-30">
        <div className="h-32 w-32 rounded-full border border-cyan-400" />
        <div className="absolute h-40 w-[1px] bg-cyan-400" />
        <div className="absolute h-[1px] w-40 bg-cyan-400" />
      </div>
    </div>
  );
}