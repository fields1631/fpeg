import pickle
import numpy as np
from fpeg.pipeline import Pipeline
from fpeg.codec import EBCOTCodec
from fpeg.transformer import DWTransformer
from fpeg.utils import *


if __name__ == "__main__":
  pipeline = Pipeline([
                      ("reader0", Reader()),
                      ("level shifter0", LevelShifter()),
                      # ("normalizer0", Normalizer()),
                      ("color transformer0", ColorTransformer()),
                      ("spliter0", Spliter()),
                      ("dw transformer0", DWTransformer()),
                      ("quantizer0", Quantizer()),
                      # ("ebcot codec0", EBCOTCodec())
                      ("quantizer1", Quantizer()),
                      ("dw transformer1", DWTransformer()),
                      ("spliter1", Spliter()),
                      ("color transformer1", ColorTransformer()),
                      # ("normalizer1", Normalizer()),
                      ("level shifter1", LevelShifter()),
                      ("writer0", Writer())
                      ],
                      params={
                      "reader0": {"flag": "color"},
                      "level shifter0": {"mode": "shift", "depth": 8},
                      # "normalizer0": {"mode": "normalize", "depth": 8},
                      "color transformer0": {"mode": "transform", "lossy": False},
                      "spliter0": {"tile_shape": (256, 256)},
                      "dw transformer0": {"mode": "forward", "lossy": False, "D": 3},
                      "quantizer0": {"mode": "quantify", "irreversible": False, "accelerated": False},
                      # "ebcot codec0": {"mode": "encode", "accelerated": False, "tile_shape": (256, 128)}
                      "quantizer1": {"mode": "dequantify", "irreversible": False, "accelerated": False},
                      "dw transformer1": {"mode": "backward", "lossy": False, "D": 3},
                      "spliter1": {"block_shape": (4, 5), "mode": "recover"},
                      "color transformer1": {"mode": "reverse transform", "lossy": False},
                      # "normalizer1": {"mode": "denormalize", "depth": 8},
                      "level shifter1": {"mode": "reverse shift", "depth": 8},
                      "writer0": {"path": r"out/out.jpg"}
                      })
  
  path = r"in/rosmontis.jpg"
  pipeline.recv(path)
  # out = pipeline.monitor.data[-1]["quantizer0"]
  print(pipeline.get_log())

  quantizer_input0 = pipeline.monitor.data[-1]["quantizer0"][0]
  quantizer_output1 = pipeline.monitor.data[-1]["quantizer1"][1]
  for tile0, tile1 in zip(quantizer_input0, quantizer_output1):
    for subbands0, subbands1 in zip(tile0, tile1):
      if isinstance(subbands0, tuple):
        print([np.max(np.abs((subband0 - subband1))) for subband0, subband1 in zip(subbands0, subbands1)])
      else:
        print(np.max(np.abs(subbands0 - subbands1)))

  dwtransformer_input0 = pipeline.monitor.data[-1]["dw transformer0"][0]
  dwtransformer_output1 = pipeline.monitor.data[-1]["dw transformer1"][1]
  for tile0, tile1 in zip(dwtransformer_input0, dwtransformer_output1):
    print(np.max(np.abs(tile0 - tile1)))

  # pickle.dump(out, open(r"out.bin", "wb"))
  #
  # out = pickle.load(open(r"out.bin", "rb"))[1]
  # pipeline = Pipeline([
  #                     # ("ebcot codec1", EBCOTCodec()),
  #                     ("quantizer1", Quantizer()),
  #                     ("dw transformer1", DWTransformer()),
  #                     ("spliter1", Spliter()),
  #                     ("color transformer1", ColorTransformer()),
  #                     # ("normalizer1", Normalizer()),
  #                     ("level shifter1", LevelShifter()),
  #                     ("writer0", Writer())
  #                     ],
  #                     params={
  #                     # "ebcot codec1": {"mode": "decode", "accelerated": False},
  #                     "quantizer1": {"mode": "dequantify", "irreversible": False, "accelerated": False},
  #                     "dw transformer1": {"mode": "backward", "lossy": False, "D": 4},
  #                     "spliter1": {"block_shape": (1, 1), "mode": "recover"},
  #                     "color transformer1": {"mode": "reverse transform", "lossy": False},
  #                     # "normalizer1": {"mode": "denormalize", "depth": 8},
  #                     "level shifter1": {"mode": "reverse shift", "depth": 8},
  #                     "writer0": {"path": r"out/out.jpg"}
  #                     })
  #
  # pipeline.recv(out)
  # print(pipeline.get_log())
