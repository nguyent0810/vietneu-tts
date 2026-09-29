// Tách chủ thể khỏi nền bằng Vision (macOS 14+), chạy cục bộ, không tải model.
// Dùng cho bố cục 2.5D của video dài: fgmask <ảnh vào> <mask PNG ra>
// In ra tỉ lệ diện tích chủ thể (0..1); không có chủ thể -> in 0 và thoát mã 2.
import Foundation
import Vision
import CoreImage
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count == 3 else { FileHandle.standardError.write("usage: fgmask in out.png\n".data(using: .utf8)!); exit(64) }
let inURL = URL(fileURLWithPath: args[1]), outURL = URL(fileURLWithPath: args[2])
guard let src = CGImageSourceCreateWithURL(inURL as CFURL, nil),
      let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else { exit(65) }
let req = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do { try handler.perform([req]) } catch { FileHandle.standardError.write("\(error)\n".data(using: .utf8)!); exit(70) }
guard let obs = req.results?.first, !obs.allInstances.isEmpty else { print("0"); exit(2) }
let buf = try obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler)
let ci = CIImage(cvPixelBuffer: buf)
let ctx = CIContext()
guard let outCG = ctx.createCGImage(ci, from: ci.extent),
      let dest = CGImageDestinationCreateWithURL(outURL as CFURL, UTType.png.identifier as CFString, 1, nil) else { exit(73) }
CGImageDestinationAddImage(dest, outCG, nil)
CGImageDestinationFinalize(dest)
// tỉ lệ diện tích chủ thể
CVPixelBufferLockBaseAddress(buf, .readOnly)
let w = CVPixelBufferGetWidth(buf), h = CVPixelBufferGetHeight(buf), rb = CVPixelBufferGetBytesPerRow(buf)
let base = CVPixelBufferGetBaseAddress(buf)!.assumingMemoryBound(to: Float32.self)
var on = 0
for y in stride(from: 0, to: h, by: 4) { for x in stride(from: 0, to: w, by: 4) { if base[y * (rb / 4) + x] > 0.5 { on += 1 } } }
CVPixelBufferUnlockBaseAddress(buf, .readOnly)
print(String(format: "%.4f", Double(on) / Double(((h + 3) / 4) * ((w + 3) / 4))))
