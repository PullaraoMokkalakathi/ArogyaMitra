export type AngleRange = {
  idealMin: number;
  idealMax: number;
  acceptableMin: number;
  acceptableMax: number;
};

export const WORKOUT_ANGLE_RANGES: Record<string, AngleRange> = {
  "pushups": {
    idealMin: 160,
    idealMax: 180,
    acceptableMin: 120,
    acceptableMax: 159,
  },
  "squats": {
    idealMin: 90,
    idealMax: 120,
    acceptableMin: 60,
    acceptableMax: 150,
  },
  "plank": {
    idealMin: 170,
    idealMax: 190,
    acceptableMin: 160,
    acceptableMax: 200,
  },
  "lunges": {
    idealMin: 80,
    idealMax: 100,
    acceptableMin: 60,
    acceptableMax: 120,
  },
  "bench press": {
    idealMin: 30,
    idealMax: 90,
    acceptableMin: 15,
    acceptableMax: 120,
  },
  "deadlift": {
    idealMin: 90,
    idealMax: 160,
    acceptableMin: 70,
    acceptableMax: 170,
  },
  "bicep curl": {
    idealMin: 40,
    idealMax: 70,
    acceptableMin: 20,
    acceptableMax: 100,
  },
  "hammer curl": {
    idealMin: 35,
    idealMax: 65,
    acceptableMin: 15,
    acceptableMax: 95,
  },
  "cable crossovers": {
    idealMin: 45,
    idealMax: 75,
    acceptableMin: 30,
    acceptableMax: 100,
  },
  "seated cable row": {
    idealMin: 80,
    idealMax: 120,
    acceptableMin: 60,
    acceptableMax: 140,
  },
  "lat pulldown": {
    idealMin: 85,
    idealMax: 110,
    acceptableMin: 70,
    acceptableMax: 130,
  },
  "tricep pushdown": {
    idealMin: 85,
    idealMax: 110,
    acceptableMin: 70,
    acceptableMax: 130,
  },
  "calf raises": {
    idealMin: 150,
    idealMax: 180,
    acceptableMin: 130,
    acceptableMax: 190,
  },
  "reverse pec deck": {
    idealMin: 60,
    idealMax: 90,
    acceptableMin: 45,
    acceptableMax: 110,
  },
  "shoulder press": {
    idealMin: 70,
    idealMax: 110,
    acceptableMin: 50,
    acceptableMax: 130,
  },
  "russian twists": {
    idealMin: 20,
    idealMax: 45,
    acceptableMin: 10,
    acceptableMax: 60,
  },
  "lateral raises": {
    idealMin: 60,
    idealMax: 100,
    acceptableMin: 40,
    acceptableMax: 120,
  },
  "chest fly": {
    idealMin: 30,
    idealMax: 70,
    acceptableMin: 20,
    acceptableMax: 90,
  },
};

export function calculateAccuracy(angle: number, workoutName: string): number {
  const normalizedName = workoutName.trim().toLowerCase();
  const range = WORKOUT_ANGLE_RANGES[normalizedName];
  
  if (!range) {
    return 60;
  }
  
  const { idealMin, idealMax, acceptableMin, acceptableMax } = range;
  
  if (angle >= idealMin && angle <= idealMax) {
    return 100;
  }
  
  if (angle >= acceptableMin && angle <= acceptableMax) {
    return 75;
  }
  
  return 40;
}