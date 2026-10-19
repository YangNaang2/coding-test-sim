// Java 하네스: Solution 클래스의 solution 메서드를 테스트 케이스마다 새 인스턴스로 호출한다.
// 사용법: java Main <케이스 JSON 경로> <시작 인덱스>
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class Main {
    static final String MARK = "@@CT@@";
    static final int OUT_LIMIT = 20000;
    static PrintStream real;

    public static void main(String[] args) throws Exception {
        real = new PrintStream(new FileOutputStream(FileDescriptor.out), true, "UTF-8");
        String text = new String(Files.readAllBytes(Paths.get(args[0])), StandardCharsets.UTF_8);
        int start = Integer.parseInt(args[1]);
        @SuppressWarnings("unchecked")
        Map<String, Object> data = (Map<String, Object>) new Parser(text).parse();
        @SuppressWarnings("unchecked")
        List<Object> cases = (List<Object>) data.get("cases");

        Method m = null;
        for (Method x : Solution.class.getDeclaredMethods()) {
            if (x.getName().equals("solution")) { m = x; break; }
        }
        if (m == null) {
            send("{\"t\":\"compile\",\"err\":" + q("Solution 클래스에 solution 메서드가 없습니다.") + "}");
            return;
        }
        m.setAccessible(true);
        Class<?>[] pt = m.getParameterTypes();

        for (int i = start; i < cases.size(); i++) {
            @SuppressWarnings("unchecked")
            List<Object> a = (List<Object>) cases.get(i);
            Object[] conv = new Object[pt.length];
            String convErr = null;
            try {
                if (a.size() != pt.length) throw new IllegalArgumentException("매개변수 개수가 다릅니다.");
                for (int k = 0; k < pt.length; k++) conv[k] = convert(a.get(k), pt[k]);
            } catch (Exception e) {
                convErr = "매개변수를 solution의 타입으로 바꿀 수 없습니다: " + e.getMessage();
            }
            send("{\"t\":\"start\",\"i\":" + i + "}");
            if (convErr != null) {
                send("{\"t\":\"res\",\"i\":" + i + ",\"ok\":false,\"kind\":\"error\",\"ms\":0,\"out\":\"\",\"err\":" + q(convErr) + "}");
                continue;
            }
            Cap cap = new Cap();
            PrintStream ps = new PrintStream(cap, true, "UTF-8");
            System.setOut(ps);
            long t0 = System.nanoTime();
            try {
                Object inst = null;
                if (!Modifier.isStatic(m.getModifiers())) {
                    Constructor<?> c = Solution.class.getDeclaredConstructor();
                    c.setAccessible(true);
                    inst = c.newInstance();
                }
                Object ret = m.invoke(inst, conv);
                double ms = (System.nanoTime() - t0) / 1e6;
                ps.flush();
                System.setOut(real);
                send("{\"t\":\"res\",\"i\":" + i + ",\"ok\":true,\"ret\":" + toJson(ret) + ",\"ms\":" + ms + ",\"out\":" + q(cap.text()) + "}");
            } catch (Throwable e) {
                double ms = (System.nanoTime() - t0) / 1e6;
                ps.flush();
                System.setOut(real);
                Throwable cause = (e instanceof InvocationTargetException && e.getCause() != null) ? e.getCause() : e;
                send("{\"t\":\"res\",\"i\":" + i + ",\"ok\":false,\"kind\":\"error\",\"ms\":" + ms + ",\"out\":" + q(cap.text()) + ",\"err\":" + q(stack(cause)) + "}");
            }
        }
    }

    static void send(String s) {
        real.print(MARK + s + "\n");
        real.flush();
    }

    static String stack(Throwable e) {
        StringBuilder sb = new StringBuilder(e.toString());
        int n = 0;
        for (StackTraceElement el : e.getStackTrace()) {
            if (el.getClassName().startsWith("Main") || el.getClassName().startsWith("java.") || el.getClassName().startsWith("jdk.")) continue;
            sb.append("\n\tat ").append(el);
            if (++n >= 20) break;
        }
        return sb.toString();
    }

    // ---------- 타입 변환 ----------
    static Object convert(Object v, Class<?> t) {
        if (t == int.class || t == Integer.class) return ((Number) v).intValue();
        if (t == long.class || t == Long.class) return ((Number) v).longValue();
        if (t == double.class || t == Double.class) return ((Number) v).doubleValue();
        if (t == boolean.class || t == Boolean.class) return (Boolean) v;
        if (t == String.class) return (String) v;
        if (t == char.class) return ((String) v).charAt(0);
        if (t.isArray()) {
            List<?> list = (List<?>) v;
            Class<?> ct = t.getComponentType();
            Object arr = Array.newInstance(ct, list.size());
            for (int k = 0; k < list.size(); k++) Array.set(arr, k, convert(list.get(k), ct));
            return arr;
        }
        if (List.class.isAssignableFrom(t)) return new ArrayList<>((List<?>) v);
        throw new IllegalArgumentException("지원하지 않는 타입 " + t.getSimpleName());
    }

    static String toJson(Object o) {
        if (o == null) return "null";
        if (o instanceof String) return q((String) o);
        if (o instanceof Character) return q(String.valueOf(o));
        if (o instanceof Boolean) return o.toString();
        if (o instanceof Double || o instanceof Float) {
            double d = ((Number) o).doubleValue();
            if (Double.isNaN(d) || Double.isInfinite(d)) return "null";
            return Double.toString(d);
        }
        if (o instanceof Number) return o.toString();
        if (o.getClass().isArray()) {
            StringBuilder sb = new StringBuilder("[");
            int n = Array.getLength(o);
            for (int k = 0; k < n; k++) {
                if (k > 0) sb.append(',');
                sb.append(toJson(Array.get(o, k)));
            }
            return sb.append(']').toString();
        }
        if (o instanceof Collection) {
            StringBuilder sb = new StringBuilder("[");
            boolean first = true;
            for (Object x : (Collection<?>) o) {
                if (!first) sb.append(',');
                sb.append(toJson(x));
                first = false;
            }
            return sb.append(']').toString();
        }
        return q(o.toString());
    }

    static String q(String s) {
        StringBuilder sb = new StringBuilder("\"");
        for (int k = 0; k < s.length(); k++) {
            char c = s.charAt(k);
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
            }
        }
        return sb.append('"').toString();
    }

    // ---------- 출력 캡처 ----------
    static class Cap extends OutputStream {
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        boolean cut = false;
        @Override public void write(int b) {
            if (buf.size() < OUT_LIMIT) buf.write(b); else cut = true;
        }
        @Override public void write(byte[] b, int off, int len) {
            int room = OUT_LIMIT - buf.size();
            if (room <= 0) { cut = true; return; }
            if (len > room) { cut = true; len = room; }
            buf.write(b, off, len);
        }
        String text() {
            return new String(buf.toByteArray(), StandardCharsets.UTF_8) + (cut ? "\n...(출력이 너무 길어 생략)" : "");
        }
    }

    // ---------- 최소 JSON 파서 ----------
    static class Parser {
        final String s;
        int p = 0;
        Parser(String s) { this.s = s; }

        Object parse() { ws(); Object v = value(); ws(); return v; }

        void ws() { while (p < s.length() && Character.isWhitespace(s.charAt(p))) p++; }

        Object value() {
            ws();
            char c = s.charAt(p);
            if (c == '{') {
                p++;
                Map<String, Object> m = new LinkedHashMap<>();
                ws();
                if (s.charAt(p) == '}') { p++; return m; }
                while (true) {
                    ws();
                    String k = str();
                    ws(); p++; // ':'
                    m.put(k, value());
                    ws();
                    if (s.charAt(p++) == '}') return m;
                }
            }
            if (c == '[') {
                p++;
                List<Object> l = new ArrayList<>();
                ws();
                if (s.charAt(p) == ']') { p++; return l; }
                while (true) {
                    l.add(value());
                    ws();
                    if (s.charAt(p++) == ']') return l;
                }
            }
            if (c == '"') return str();
            if (s.startsWith("true", p)) { p += 4; return Boolean.TRUE; }
            if (s.startsWith("false", p)) { p += 5; return Boolean.FALSE; }
            if (s.startsWith("null", p)) { p += 4; return null; }
            int st = p;
            boolean frac = false;
            while (p < s.length() && "+-0123456789.eE".indexOf(s.charAt(p)) >= 0) {
                char d = s.charAt(p);
                if (d == '.' || d == 'e' || d == 'E') frac = true;
                p++;
            }
            String num = s.substring(st, p);
            if (!frac) {
                try { return Long.parseLong(num); } catch (NumberFormatException e) { return Double.parseDouble(num); }
            }
            return Double.parseDouble(num);
        }

        String str() {
            StringBuilder sb = new StringBuilder();
            p++; // opening quote
            while (true) {
                char c = s.charAt(p++);
                if (c == '"') return sb.toString();
                if (c == '\\') {
                    char e = s.charAt(p++);
                    switch (e) {
                        case 'n': sb.append('\n'); break;
                        case 't': sb.append('\t'); break;
                        case 'r': sb.append('\r'); break;
                        case 'b': sb.append('\b'); break;
                        case 'f': sb.append('\f'); break;
                        case 'u': sb.append((char) Integer.parseInt(s.substring(p, p + 4), 16)); p += 4; break;
                        default: sb.append(e);
                    }
                } else sb.append(c);
            }
        }
    }
}
